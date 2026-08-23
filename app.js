const state={rows:[],filtered:[],page:1,pageSize:50};
const weekdays=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];
const courts={"Court 1":"Court 1 - Astro","Court 2":"Court 2 - Astro","Court 3":"Court 3 - Astro","Court 4":"Court 4 - Clay","Court 5":"Court 5 - Astro","Court 6":"Court 6 - Astro","Court 7":"Court 7 - Clay","Ball Machine":"Ball Machine","Table Tennis":"Table Tennis Table"};
const els=Object.fromEntries(["status","totalBookings","courtCount","categoryCount","bookedHours","searchInput","courtMenu","courtSummary","courtOptions","categoryFilter","startDate","endDate","weekdayFilter","periodFilter","typeFilter","membershipFilter","clearFilters","courtChart","categoryChart","weekdayChart","shownCount","bookingRows","previousPage","nextPage","pageStatus"].map(id=>[id,document.getElementById(id)]));

function text(value){return String(value??"").trim()}
function normal(value){return text(value).toLocaleLowerCase()}
function unique(key){return [...new Set(state.rows.map(row=>text(row[key])).filter(Boolean))].sort((a,b)=>a.localeCompare(b,undefined,{numeric:true}))}
function addOptions(select,values){values.forEach(value=>select.add(new Option(value,value)))}
function localDate(dateValue){const date=new Date(`${dateValue}T12:00:00`);return Number.isNaN(date.getTime())?dateValue:new Intl.DateTimeFormat("en-GB",{day:"2-digit",month:"short",year:"numeric"}).format(date)}
function weekday(dateValue){const date=new Date(`${dateValue}T12:00:00`);return Number.isNaN(date.getTime())?"":weekdays[(date.getDay()+6)%7]}
function period(timeValue){const match=text(timeValue).match(/^(\d{1,2}):(\d{2})/);if(!match)return "";const minutes=Number(match[1])*60+Number(match[2]);return minutes<720?"Morning":minutes<=1020?"Afternoon":"Evening"}
function number(value){const parsed=Number(value);return Number.isFinite(parsed)?parsed:0}
function countBy(rows,key,order=[]){const counts=new Map();rows.forEach(row=>{const value=key(row);if(value)counts.set(value,(counts.get(value)||0)+1)});const entries=[...counts.entries()];return order.length?order.filter(item=>counts.has(item)).map(item=>[item,counts.get(item)]):entries.sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0],undefined,{numeric:true}))}
function courtCounts(rows,selected=[]){return Object.entries(courts).filter(([label])=>!selected.length||selected.includes(label)).map(([label,match])=>[label,rows.filter(row=>normal(row.court).includes(normal(match))).length]).filter(([,count])=>count>0)}
function selectedCourts(){return [...els.courtOptions.querySelectorAll('input[data-court]:checked')].map(input=>input.value)}
function updateCourtSummary(){const selected=selectedCourts();els.courtSummary.textContent=!selected.length?"All courts":selected.length===1?selected[0]:`${selected.length} courts selected`}
function displayedCourts(row,selected){return selected.length?selected.filter(court=>normal(row.court).includes(normal(courts[court]))).join(", "):row.court}

function renderChart(container,entries){if(!entries.length){container.innerHTML='<p class="empty-chart">No data for this selection.</p>';return}const max=Math.max(...entries.map(([,value])=>value),1);container.innerHTML=entries.map(([label,value])=>`<div class="bar-item" title="${escapeHtml(label)}: ${value.toLocaleString()}"><span class="bar-value">${value.toLocaleString()}</span><span class="bar" style="height:${Math.max(2,value/max*100)}%"></span><span class="bar-label">${escapeHtml(label)}</span></div>`).join("")}
function escapeHtml(value){const node=document.createElement("div");node.textContent=text(value);return node.innerHTML}

function applyFilters(){
  const query=normal(els.searchInput.value);
  const chosenCourts=selectedCourts();
  state.filtered=state.rows.filter(row=>{
    if(query&&!normal(Object.values(row).join(" ")).includes(query))return false;
    if(chosenCourts.length&&!chosenCourts.some(court=>normal(row.court).includes(normal(courts[court]))))return false;
    if(els.categoryFilter.value!==""&&row.category!==els.categoryFilter.value)return false;
    if(els.startDate.value&&row.date<els.startDate.value)return false;
    if(els.endDate.value&&row.date>els.endDate.value)return false;
    if(els.weekdayFilter.value&&weekday(row.date)!==els.weekdayFilter.value)return false;
    if(els.periodFilter.value&&period(row.time)!==els.periodFilter.value)return false;
    if(els.typeFilter.value&&row.bookingType!==els.typeFilter.value)return false;
    if(els.membershipFilter.value&&row.membershipStatus!==els.membershipFilter.value)return false;
    return true;
  });
  const pageTotal=Math.max(1,Math.ceil(state.filtered.length/state.pageSize));if(state.page>pageTotal)state.page=pageTotal;
  render(pageTotal);
}

function render(pageTotal){
  const chosenCourts=selectedCourts();
  els.totalBookings.textContent=state.filtered.length.toLocaleString();
  const visibleCourts=courtCounts(state.filtered,chosenCourts);els.courtCount.textContent=visibleCourts.length.toLocaleString();
  els.categoryCount.textContent=new Set(state.filtered.map(row=>row.category).filter(Boolean)).size.toLocaleString();
  const minutes=state.filtered.reduce((sum,row)=>sum+number(row.duration),0);els.bookedHours.textContent=(minutes/60).toLocaleString(undefined,{maximumFractionDigits:1});
  renderChart(els.courtChart,visibleCourts);
  renderChart(els.categoryChart,countBy(state.filtered,row=>row.category));
  renderChart(els.weekdayChart,countBy(state.filtered,row=>weekday(row.date),weekdays));
  const start=(state.page-1)*state.pageSize;const visible=state.filtered.slice(start,start+state.pageSize);
  els.bookingRows.innerHTML=visible.length?visible.map(row=>`<tr><td>${escapeHtml(localDate(row.date))}</td><td>${escapeHtml(displayedCourts(row,chosenCourts))}</td><td>${escapeHtml(row.category)}</td><td>${number(row.duration).toLocaleString()} min</td><td>${escapeHtml(row.time)}</td><td>${escapeHtml(row.bookingType)}</td><td>${escapeHtml(row.membershipStatus)}</td></tr>`).join(""):'<tr><td colspan="7">No bookings match these filters.</td></tr>';
  els.shownCount.textContent=`${state.filtered.length.toLocaleString()} of ${state.rows.length.toLocaleString()} shown`;
  els.pageStatus.textContent=`Page ${state.page} of ${pageTotal}`;els.previousPage.disabled=state.page<=1;els.nextPage.disabled=state.page>=pageTotal;
}

function configureFilters(){
  els.courtOptions.innerHTML=`<label><input type="checkbox" data-all-courts checked> All courts</label>${Object.keys(courts).map(court=>`<label><input type="checkbox" data-court value="${court}"> ${court}</label>`).join("")}`;
  addOptions(els.categoryFilter,unique("category"));addOptions(els.typeFilter,unique("bookingType"));addOptions(els.membershipFilter,unique("membershipStatus"));addOptions(els.weekdayFilter,weekdays);
  const dates=state.rows.map(row=>row.date).filter(Boolean).sort();if(dates.length){els.startDate.min=dates[0];els.startDate.max=dates.at(-1);els.endDate.min=dates[0];els.endDate.max=dates.at(-1)}
}

function bindEvents(){
  [els.searchInput,els.categoryFilter,els.startDate,els.endDate,els.weekdayFilter,els.periodFilter,els.typeFilter,els.membershipFilter].forEach(control=>control.addEventListener(control.tagName==="INPUT"?"input":"change",()=>{state.page=1;applyFilters()}));
  els.courtOptions.addEventListener("change",event=>{const all=els.courtOptions.querySelector("[data-all-courts]");const choices=[...els.courtOptions.querySelectorAll("[data-court]")];if(event.target===all){all.checked=true;choices.forEach(choice=>choice.checked=false)}if(event.target.matches("[data-court]")){all.checked=false;if(!choices.some(choice=>choice.checked))all.checked=true}updateCourtSummary();state.page=1;applyFilters()});
  els.clearFilters.addEventListener("click",()=>{[els.searchInput,els.categoryFilter,els.startDate,els.endDate,els.weekdayFilter,els.periodFilter,els.typeFilter,els.membershipFilter].forEach(control=>control.value="");els.courtOptions.querySelector("[data-all-courts]").checked=true;els.courtOptions.querySelectorAll("[data-court]").forEach(choice=>choice.checked=false);updateCourtSummary();state.page=1;applyFilters()});
  els.previousPage.addEventListener("click",()=>{if(state.page>1){state.page-=1;applyFilters();document.getElementById("bookings").scrollIntoView()}});
  els.nextPage.addEventListener("click",()=>{if(state.page*state.pageSize<state.filtered.length){state.page+=1;applyFilters();document.getElementById("bookings").scrollIntoView()}});
}

async function initialise(){
  try{const response=await fetch(`data/bookings.json?v=${Date.now()}`,{cache:"no-store"});if(!response.ok)throw new Error(`Data request failed (${response.status})`);const payload=await response.json();if(!Array.isArray(payload.rows))throw new Error("Booking data is invalid");state.rows=payload.rows;state.filtered=payload.rows.slice();configureFilters();bindEvents();applyFilters();const refreshed=payload.generatedAt?new Intl.DateTimeFormat("en-GB",{dateStyle:"medium",timeStyle:"short"}).format(new Date(payload.generatedAt)):"unknown";els.status.textContent=`Last refreshed ${refreshed} · ${state.rows.length.toLocaleString()} sanitised booking records.`}catch(error){els.status.textContent=`Booking data could not be loaded: ${error.message}`;render(1)}}
initialise();
