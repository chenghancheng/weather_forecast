async function getJSON(url){
	const res = await fetch(url);
	if(!res.ok) throw new Error("网络错误: "+res.status);
	return await res.json();
}

const adviceEl = document.getElementById('result');
const cardsEl = document.getElementById('cards');
let histChart;

function i18nDict(){
	return {
		zh:{
			"assistant.title":"生活助手",
			"assistant.placeholder":"问我：明天/后天穿什么？ 要不要带伞？",
			"assistant.send":"发送",
			"extremes.title":"未来极端天气",
			"forecast.title":"未来7天预报",
			"history.title":"近14天（气温&降水）",
			"history.hint":"数据不对？",
			"theme.system":"系统","theme.light":"浅色","theme.dark":"深色",
			"tips.unknown":"请换个方式问问吧",
			"label.precip":"降水",
			"label.humidity":"湿度",
			"label.wind":"风速",
			"risk.high":"高风险",
			"risk.low":"低风险",
			"search.placeholder":"搜索城市(中文/拼音/English)"
		},
		en:{
			"assistant.title":"Life Assistant",
			"assistant.placeholder":"Ask: what to wear tomorrow? need umbrella?",
			"assistant.send":"Send",
			"extremes.title":"Extreme Weather (Next 7d)",
			"forecast.title":"7-Day Forecast",
			"history.title":"Past 14d (Temp & Precip)",
			"history.hint":"Refresh",
			"theme.system":"System","theme.light":"Light","theme.dark":"Dark",
			"tips.unknown":"Try asking in another way",
			"label.precip":"Precip",
			"label.humidity":"Humidity",
			"label.wind":"Wind",
			"risk.high":"High Risk",
			"risk.low":"Low Risk",
			"search.placeholder":"Search city (Chinese/Pinyin/English)"
		}
	};
}

function t(key){
	const langSel=document.getElementById('lang');
	const lang=(langSel?.value)||'zh';
	return (i18nDict()[lang]||i18nDict().zh)[key]||key;
}

function applyI18n(){
	document.getElementById('title-assistant').textContent=t('assistant.title');
	document.getElementById('title-extremes').textContent=t('extremes.title');
	document.getElementById('title-forecast').textContent=t('forecast.title');
	document.getElementById('title-history').textContent=t('history.title');
	const input=document.getElementById('query');
	input.placeholder=t('assistant.placeholder');
	const send=document.getElementById('btn-send');
	send.textContent=t('assistant.send');
	// options text
	const theme=document.getElementById('theme');
	if(theme){
		const opts=theme.options;
		opts[0].textContent=t('theme.system');
		opts[1].textContent=t('theme.light');
		opts[2].textContent=t('theme.dark');
	}
	// translate city labels when en
	const langSel=document.getElementById('lang');
	const citySel=document.getElementById('city');
	if(langSel && citySel){
		const enMap={"北京":"Beijing","上海":"Shanghai","广州":"Guangzhou","深圳":"Shenzhen","杭州":"Hangzhou","成都":"Chengdu","天津":"Tianjin","南京":"Nanjing","武汉":"Wuhan","西安":"Xi'an","重庆":"Chongqing","苏州":"Suzhou","青岛":"Qingdao","沈阳":"Shenyang","大连":"Dalian","厦门":"Xiamen","南宁":"Nanning"};
		for(const opt of citySel.options){ opt.textContent = (langSel.value==='en') ? (enMap[opt.value]||opt.value) : opt.value; }
	}
	const cs=document.getElementById('city-search'); if(cs){ cs.placeholder=t('search.placeholder'); }
}

function showText(text){ if(adviceEl) adviceEl.textContent = text; }

function renderAdvice(obj){
	if(!adviceEl) return;
	if(!obj){ adviceEl.textContent=''; return; }
	if(obj.intent === 'unknown'){ adviceEl.textContent = t('tips.unknown'); return; }
	if(obj.intent === 'umbrella'){
		adviceEl.innerHTML = `<div class="title">(${obj.for_date})</div><ul class="items"><li>${obj.advice}</li></ul>`; return;
	}
	if(obj.intent === 'sunscreen'){
		adviceEl.innerHTML = `<div class="title">(${obj.for_date})</div><ul class="items"><li>${obj.advice}</li></ul>`; return;
	}
	if(obj.intent === 'outfit_tomorrow' || obj.intent === 'outfit_day'){
		const lines = [];
		lines.push(`<div class="title">(${obj.for_date})</div>`);
		lines.push(`<div>气温 ${obj.temperature_c?.toFixed?.(1)}°C (↑${obj.tmax?.toFixed?.(1)} ↓${obj.tmin?.toFixed?.(1)})，降水 ${obj.precipitation_mm?.toFixed?.(1)} mm</div>`);
		if(Array.isArray(obj.advice)){
			lines.push('<ul class="items">'+obj.advice.map(a=>`<li>${a}</li>`).join('')+'</ul>');
		}
		adviceEl.innerHTML = lines.join('');
		return;
	}
	adviceEl.textContent = t('tips.unknown');
}

function card(item){
	const lp=t('label.precip'), lh=t('label.humidity'), lw=t('label.wind');
	const isRainy = Number(item.precipitation_mm||0) >= 1.0;
	const cls = isRainy ? 'weather-rainy' : 'weather-sunny';
	const icon = isRainy
		? '<svg class="weather-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M7 15c-2.2 0-4-1.8-4-4 0-2 1.5-3.7 3.4-3.9C7 4.6 8.9 3 11.1 3c2.5 0 4.6 1.9 4.9 4.3 2.1.3 3.8 2.1 3.8 4.2 0 2.4-2 4.4-4.4 4.4H7z" fill="currentColor" opacity=".9"/><g stroke="currentColor" stroke-linecap="round"><path d="M9 18v3"/><path d="M13 18v3"/><path d="M17 18v3"/></g></svg>'
		: '<svg class="weather-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="5" fill="currentColor" opacity=".9"/><g stroke="currentColor" stroke-linecap="round"><path d="M12 1v3"/><path d="M12 20v3"/><path d="M1 12h3"/><path d="M20 12h3"/><path d="M4.2 4.2l2.1 2.1"/><path d="M17.7 17.7l2.1 2.1"/><path d="M19.8 4.2l-2.1 2.1"/><path d="M6.3 17.7l-2.1 2.1"/></g></svg>';
	return `
		<div class="card ${cls}">
			<div class="date">${item.date} ${icon}</div>
			<div class="temp">${item.temperature_c.toFixed(1)}°C <span style="color:var(--muted);font-size:12px">(↑${item.tmax?.toFixed?.(1)} ↓${item.tmin?.toFixed?.(1)})</span></div>
			<div class="meta">${lp}：${item.precipitation_mm.toFixed(1)} mm<br/>${lh}：${item.humidity.toFixed(0)}%　${lw}：${item.wind_speed_ms.toFixed(1)} m/s</div>
			<button class="data-source-btn" onclick="showDataSource('${item.date}', ${JSON.stringify(item.calculation_details || {})})" title="查看数据来源">i</button>
		</div>
	`;
}

// 数据来源模态框相关函数
function showDataSource(date, details) {
	const modal = document.getElementById('dataSourceModal');
	const content = document.getElementById('dataSourceContent');
	
	let html = `<div class="data-source-item">
		<div class="data-source-item-title">${date} 预测数据来源</div>`;
	
	if (details.data_source === 'external_fusion') {
		html += `
		<div class="data-source-grid">
			<div class="data-source-value">
				<div class="data-source-value-label">官方预测温度</div>
				<div class="data-source-value-number">${details.external_temp?.toFixed(1) || 'N/A'}°C</div>
			</div>
			<div class="data-source-value">
				<div class="data-source-value-label">本地模型温度</div>
				<div class="data-source-value-number">${details.local_temp?.toFixed(1) || 'N/A'}°C</div>
			</div>
		</div>
		<div class="data-source-grid">
			<div class="data-source-value">
				<div class="data-source-value-label">官方预测降水</div>
				<div class="data-source-value-number">${details.external_prec?.toFixed(1) || 'N/A'} mm</div>
			</div>
			<div class="data-source-value">
				<div class="data-source-value-label">本地模型降水</div>
				<div class="data-source-value-number">${details.local_prec?.toFixed(1) || 'N/A'} mm</div>
			</div>
		</div>
		<div class="data-source-formula">
			最终温度 = 官方预测 × ${details.weights.external} + 本地模型 × ${details.weights.local}<br>
			最终降水 = 官方预测 × ${details.weights.external} + 本地模型 × ${details.weights.local}
		</div>`;
	} else {
		html += `
		<div class="data-source-grid">
			<div class="data-source-value">
				<div class="data-source-value-label">本地模型温度</div>
				<div class="data-source-value-number">${details.local_temp?.toFixed(1) || 'N/A'}°C</div>
			</div>
			<div class="data-source-value">
				<div class="data-source-value-label">本地模型降水</div>
				<div class="data-source-value-number">${details.local_prec?.toFixed(1) || 'N/A'} mm</div>
			</div>
		</div>
		<div class="data-source-formula">
			仅使用本地模型预测（ARIMA + LSTM融合）
		</div>`;
	}
	
	html += '</div>';
	content.innerHTML = html;
	modal.classList.add('show');
}

function closeDataSourceModal() {
	const modal = document.getElementById('dataSourceModal');
	modal.classList.remove('show');
}

// 点击模态框外部关闭
document.addEventListener('DOMContentLoaded', function() {
	const modal = document.getElementById('dataSourceModal');
	modal.addEventListener('click', function(e) {
		if (e.target === modal) {
			closeDataSourceModal();
		}
	});
});

// 存储最新的预报数据，用于历史图表
let latestForecastData = [];

async function renderForecast(){
	try{
		const data = await getJSON(`/api/forecast?city=${encodeURIComponent(currentCity())}&days=7`);
		const list = data.forecast || [];
		latestForecastData = list; // 保存预报数据
		cardsEl.innerHTML = list.map(card).join('');
	}catch(e){
		cardsEl.innerHTML = `<div class="card">${String(e)}</div>`;
	}
}

async function renderHistory(){
	try{
		const data = await getJSON(`/api/history?city=${encodeURIComponent(currentCity())}&days=14`);
		let list = data.history || [];
		
		// 如果有预报数据，将前7天替换为预报数据以确保一致性
		if (latestForecastData.length > 0) {
			const forecastDates = new Set(latestForecastData.map(f => f.date));
			const updatedList = list.map(item => {
				const dateStr = typeof item.date === 'string' ? item.date : item.date.toISOString().split('T')[0];
				if (forecastDates.has(dateStr)) {
					const forecast = latestForecastData.find(f => f.date === dateStr);
					if (forecast) {
						return {
							...item,
							temperature_c: forecast.temperature_c,
							precipitation_mm: forecast.precipitation_mm,
							humidity: forecast.humidity,
							wind_speed_ms: forecast.wind_speed_ms
						};
					}
				}
				return item;
			});
			list = updatedList;
		}
		
		const labels = list.map(x=>x.date);
		const temps = list.map(x=>x.temperature_c);
		const precs = list.map(x=>x.precipitation_mm);
		const ctx = document.getElementById('histChart');
		if(histChart) histChart.destroy();
		const styles = getComputedStyle(document.documentElement);
		const textColor = styles.getPropertyValue('--fg').trim() || '#111827';
		const gridColor = styles.getPropertyValue('--card-border').trim() || '#e5e7eb';
		const precipLabel = t('label.precip')+" (mm)";
		const tempLabel = 'Temp (°C)';
		histChart = new Chart(ctx, {
			type: 'bar',
			data: { labels, datasets: [
				{ label:precipLabel, data:precs, yAxisID:'y1', backgroundColor:'rgba(16,185,129,.35)', borderColor:'#10b981' },
				{ label:tempLabel, data:temps, type:'line', yAxisID:'y', borderColor:'#3b82f6', backgroundColor:'rgba(59,130,246,.15)', tension:.3, fill:true },
			] },
			options: { interaction:{ intersect:false, mode:'index' }, plugins:{ legend:{display:true, labels:{color:textColor} } }, scales:{ x:{ ticks:{color:textColor}, grid:{color:gridColor} }, y:{ position:'left', ticks:{color:textColor}, grid:{color:gridColor}, title:{display:true,text:'°C',color:textColor} }, y1:{ position:'right', grid:{drawOnChartArea:false,color:gridColor}, ticks:{color:textColor}, title:{display:true,text:'mm',color:textColor} } } }
		});
	}catch(e){ showText(String(e)); }
}

function extremeCard(x){
	const badge = (x.level === '高风险' || x.level === 'High') ? `<span class="badge badge-high">${t('risk.high')}</span>` : `<span class="badge badge-low">${t('risk.low')}</span>`;
	const chips = (x.reasons||[]).map(r=>`<span class="chip">${r}</span>`).join('');
	return `<div class="extreme-card"><div class="extreme-top"><div class="extreme-date">${x.date}</div>${badge}</div><div class="extreme-meta">↑${(x.tmax||0).toFixed?.(1)}°C ↓${(x.tmin||0).toFixed?.(1)}°C · ${t('label.precip')} ${(x.precipitation_mm||0).toFixed?.(1)}mm</div><div class="chips">${chips}</div></div>`;
}

async function renderExtremes(){
	const el = document.getElementById('extremes');
	if(!el) return;
	try{
		const data = await getJSON(`/api/alerts/summary?city=${encodeURIComponent(currentCity())}&days=7`);
		const list = data.extremes || [];
		if(list.length===0){ el.innerHTML = '<div class="extreme-card">--</div>'; return; }
		el.innerHTML = list.map(extremeCard).join('');
	}catch(e){ el.innerHTML = `<div class="extreme-card">${String(e)}</div>`; }
}

// Theme switching with system + persistence
function applyTheme(value){
	let theme=value;
	if(theme==='system'){
		theme = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
	}
	document.documentElement.setAttribute('data-theme', theme==='dark' ? 'dark':'light');
	localStorage.setItem('theme', value); // 记住用户选择（原值 system/light/dark）
}

const themeSel = document.getElementById('theme');
if(themeSel){
	// 初始化
	const saved = localStorage.getItem('theme') || 'system';
	themeSel.value=saved;
	applyTheme(saved);
	window.matchMedia('(prefers-color-scheme: dark)')?.addEventListener?.('change',()=>{
		if((localStorage.getItem('theme')||'system')==='system') applyTheme('system');
	});
	// 切换
	themeSel.addEventListener('change', ()=> applyTheme(themeSel.value));
	// 主题变更后重绘图表以应用颜色
	themeSel.addEventListener('change', ()=> renderHistory());
}

// Language switch
const langSel=document.getElementById('lang');
if(langSel){ langSel.addEventListener('change', ()=> { applyI18n(); refreshData(); }); }

// City change triggers refresh
const citySel = document.getElementById('city');
if(citySel){ citySel.addEventListener('change', ()=>{ refreshData(); }); }

// Geolocation to city mapping with IP fallback
async function geoIpFallback(){
	// 优先走后端代理，避免浏览器跨域/缓存等问题
	try{
		const j = await getJSON('/api/ip-city');
		return j.normalized || j.city || null;
	}catch(e){ return null; }
}

function normalizeCityName(name){
	return (name||'').replace(/[\s]/g,'').replace(/(市|区|县)$/,'');
}

function ensureCityOption(value){
	const sel=document.getElementById('city');
	if(!sel) return;
	let opt=[...sel.options].find(o=>o.value===value);
	if(!opt){ opt=new Option(value,value); sel.add(opt); }
	sel.value=value;
}

async function resolveChineseCityName(name){
	try{ const arr = await geocode(name); if(arr.length>0){ return arr[0].name || arr[0].display.split('·')[0]; } }catch(e){}
	return name;
}

async function initGeolocation(){
	try{
		if(localStorage.getItem('city')) return; // 已设置过
		let chosen = await geoIpFallback();
		if(!chosen && navigator.geolocation){
			await new Promise((resolve)=>{
				navigator.geolocation.getCurrentPosition((pos)=>{
					const lat=pos.coords.latitude, lon=pos.coords.longitude;
					const cityList=['北京','上海','广州','深圳','杭州','成都','天津','南京','武汉','西安','重庆','苏州','青岛','沈阳','大连','厦门','南宁'];
					const coords={
						'北京':[39.9042,116.4074],'上海':[31.2304,121.4737],'广州':[23.1291,113.2644],'深圳':[22.5431,114.0579],'杭州':[30.2741,120.1551],'成都':[30.5728,104.0668],'天津':[39.3434,117.3616],'南京':[32.0603,118.7969],'武汉':[30.5928,114.3055],'西安':[34.3416,108.9398],'重庆':[29.563,106.5516],'苏州':[31.2989,120.5853],'青岛':[36.0662,120.3826],'沈阳':[41.8057,123.4315],'大连':[38.914,121.6147],'厦门':[24.4798,118.0894],'南宁':[22.817,108.3669]
					};
					let best='北京',bestd=1e9;for(const c of cityList){const [clat,clon]=coords[c];const d=Math.hypot(clat-lat,clon-lon);if(d<bestd){bestd=d;best=c;}}
					chosen=best; resolve();
				},()=>resolve());
			});
		}
		if(chosen){
			const cn = normalizeCityName(await resolveChineseCityName(chosen));
			ensureCityOption(cn);
			localStorage.setItem('city', cn);
			await refreshData();
		}
	}catch(e){}
}

function restoreCity(){
	const saved = localStorage.getItem('city');
	const lbl = document.getElementById('city-label');
	if(saved){
		citySel.value = saved;
		if(lbl){ lbl.textContent = saved; }
		return;
	}
	// 若无历史记录或值为空，默认选中“北京”并同步到标签与本地存储
	if(!citySel.value){ citySel.value = '北京'; }
	if(lbl){ lbl.textContent = citySel.value || '北京'; }
	localStorage.setItem('city', citySel.value || '北京');
}
if(citySel){ citySel.addEventListener('change',()=> localStorage.setItem('city',citySel.value)); }

const btnSend = document.getElementById('btn-send');
if(btnSend){
	btnSend.addEventListener('click', async ()=>{
		const raw = (document.getElementById('query').value||'').trim();
		if(!raw){ showText(t('tips.unknown')); return; }
		try{ renderAdvice(await getJSON(`/api/nlp?q=${encodeURIComponent(raw)}&city=${encodeURIComponent(currentCity())}`)); }
		catch(e){ showText(t('tips.unknown')); }
	});
}

async function refreshData(){
	applyI18n();
	const overlay = document.getElementById('loader');
	if(overlay) overlay.style.display = 'flex';
	try{
		await renderForecast();
		await renderHistory();
		await renderExtremes();
	} finally {
		if(overlay) overlay.style.display = 'none';
	}
}

(async function init(){
	applyI18n();
	// 先尝试服务端基于 IP 的定位，再回落到本地默认/历史
	try{ await initGeolocation(); }catch(e){}
	restoreCity();
	await refreshData();
})();

// City search + geocoding
const cityInput=document.getElementById('city-search');
const cityDatalist=document.getElementById('city-suggestions');
let citySearchTimer;
async function geocode(q){
	if(!q) return [];
	const url=`https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(q)}&language=zh&count=8`;
	try{ const j=await getJSON(url); return (j.results||[]).map(r=>({name:r.name,admin:r.admin1,country:r.country,display:`${r.name}${r.admin1?(' · '+r.admin1):''} · ${r.country}`})); }catch(e){ return []; }
}
function setCity(v){
	if(!v) return;
	const name = normalizeCityName(v);
	const sel=document.getElementById('city');
	let opt=[...sel.options].find(o=>o.value===name);
	if(!opt){ opt=new Option(name,name); sel.add(opt); }
	sel.value=name; localStorage.setItem('city',name); refreshData();
	const lbl=document.getElementById('city-label'); if(lbl){ lbl.textContent=name; }
}
if(cityInput){
	cityInput.addEventListener('input',()=>{
		clearTimeout(citySearchTimer);
		const q=cityInput.value.trim();
		citySearchTimer=setTimeout(async ()=>{
			const arr=await geocode(q);
			cityDatalist.innerHTML=arr.map(x=>`<option value="${x.name}">${x.display}</option>`).join('');
		},300);
	});
	cityInput.addEventListener('change',()=>{ setCity(cityInput.value.trim()); cityInput.value=''; });
	cityInput.addEventListener('keydown', (e)=>{ if(e.key==='Enter'){ setCity(cityInput.value.trim()); cityInput.blur(); }});
}

// IP 城市按钮：点击后查询并切换
const btnIp = document.getElementById('btn-ip-city');
if(btnIp){
	btnIp.addEventListener('click', async ()=>{
		btnIp.disabled = true;
		try{
			const city = await geoIpFallback();
			if(city){ setCity(city); }
		}finally{ btnIp.disabled = false; }
	});
}

function qs(id){ return document.getElementById(id); }
function currentCity(){ return qs('city')?.value || '北京'; }
