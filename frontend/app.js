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

// 翻译函数
function t(key) {
	const lang = document.getElementById('lang')?.value || 'zh';
	const translations = {
		zh: {
			'assistant.title': '生活助手',
			'assistant.placeholder': '问我：明天/后天穿什么？ 要不要带伞？',
			'assistant.send': '发送',
			'assistant.sending': '发送中...',
			'extremes.title': '未来极端天气',
			'forecast.title': '未来7天预报',
			'history.title': '近14天（气温&降水）',
			'risk.high': '高风险',
			'risk.low': '低风险',
			'label.precip': '降水',
			'label.humidity': '湿度',
			'label.wind': '风速',
			'weather.heavy_rain': '强降水',
			'weather.extreme_cold': '极端低温',
			'weather.extreme_heat': '极端高温',
			'weather.strong_wind': '大风',
			'weather.high_risk': '综合风险较高',
			'data.source': '数据来源',
			'data.official_temp': '官方温度',
			'data.local_temp': '本地温度',
			'data.official_precip': '官方降水',
			'data.local_precip': '本地降水',
			'data.final_value': '最终值',
			'data.official': '官方',
			'data.local': '本地',
			'data.local_model_only': '仅本地模型'
		},
		en: {
			'assistant.title': 'Life Assistant',
			'assistant.placeholder': 'Ask me: What to wear tomorrow? Need umbrella?',
			'assistant.send': 'Send',
			'assistant.sending': 'Sending...',
			'extremes.title': 'Extreme Weather (Next 7d)',
			'forecast.title': '7-Day Forecast',
			'history.title': 'Recent 14 Days (Temp & Precip)',
			'risk.high': 'HIGH RISK',
			'risk.low': 'LOW RISK',
			'label.precip': 'Precip',
			'label.humidity': 'Humidity',
			'label.wind': 'Wind',
			'weather.heavy_rain': 'Heavy Rain',
			'weather.extreme_cold': 'Extreme Cold',
			'weather.extreme_heat': 'Extreme Heat',
			'weather.strong_wind': 'Strong Wind',
			'weather.high_risk': 'High Risk',
			'data.source': 'Data Source',
			'data.official_temp': 'Official Temp',
			'data.local_temp': 'Local Temp',
			'data.official_precip': 'Official Precip',
			'data.local_precip': 'Local Precip',
			'data.final_value': 'Final Value',
			'data.official': 'Official',
			'data.local': 'Local',
			'data.local_model_only': 'Local Model Only'
		}
	};
	return translations[lang]?.[key] || key;
}

// 翻译天气原因标签
function translateWeatherReason(reason) {
	const lang = document.getElementById('lang')?.value || 'zh';
	const translations = {
		'强降水': 'Heavy Rain',
		'极端低温': 'Extreme Cold',
		'极端高温': 'Extreme Heat',
		'大风': 'Strong Wind',
		'综合风险较高': 'High Risk'
	};
	return lang === 'en' ? (translations[reason] || reason) : reason;
}

// 应用翻译到页面
function applyI18n() {
	// 翻译标题
	const titleAssistant = document.getElementById('title-assistant');
	if (titleAssistant) titleAssistant.textContent = t('assistant.title');
	
	const titleExtremes = document.getElementById('title-extremes');
	if (titleExtremes) titleExtremes.textContent = t('extremes.title');
	
	const titleForecast = document.getElementById('title-forecast');
	if (titleForecast) titleForecast.textContent = t('forecast.title');
	
	const titleHistory = document.getElementById('title-history');
	if (titleHistory) titleHistory.textContent = t('history.title');
	
	// 翻译输入框占位符
	const queryInput = document.getElementById('query');
	if (queryInput) queryInput.placeholder = t('assistant.placeholder');
	
	// 翻译按钮
	const sendButton = document.getElementById('btn-send');
	if (sendButton) sendButton.textContent = t('assistant.send');
	
	// 翻译模态框标题
	const modalTitle = document.getElementById('modal-title');
	if (modalTitle) modalTitle.textContent = t('data.source');
	
	// 重新渲染极端天气和预报
	renderExtremes();
	renderForecast();
	renderHistory();
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
		: '<svg class="weather-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="5" fill="currentColor" opacity=".9"/><path d="M12 1v3M12 20v3M1 12h3M20 12h3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M19.8 4.2l-2.1 2.1M6.3 17.7l-2.1 2.1" stroke="currentColor" stroke-linecap="round"/></svg>';
	
	const details = item.calculation_details || {};
	let backContent = '';
	
	if (details.data_source === 'external_fusion') {
		backContent = `
			<div class="card-back-title">${t('data.source')}</div>
			<div class="data-source-grid">
				<div class="data-source-item">
					<div class="data-source-label">${t('data.official_temp')}</div>
					<div class="data-source-value">${details.external_temp?.toFixed(1) || 'N/A'}°C</div>
				</div>
				<div class="data-source-item">
					<div class="data-source-label">${t('data.local_temp')}</div>
					<div class="data-source-value">${details.local_temp?.toFixed(1) || 'N/A'}°C</div>
				</div>
			</div>
			<div class="data-source-grid">
				<div class="data-source-item">
					<div class="data-source-label">${t('data.official_precip')}</div>
					<div class="data-source-value">${details.external_prec?.toFixed(1) || 'N/A'}mm</div>
				</div>
				<div class="data-source-item">
					<div class="data-source-label">${t('data.local_precip')}</div>
					<div class="data-source-value">${details.local_prec?.toFixed(1) || 'N/A'}mm</div>
				</div>
			</div>
			<div class="data-source-formula">
				<span class="highlight">${t('data.final_value')}</span> = ${t('data.official')}×${details.weights.external} + ${t('data.local')}×${details.weights.local}
			</div>`;
	} else {
		backContent = `
			<div class="card-back-title">${t('data.source')}</div>
			<div class="data-source-grid">
				<div class="data-source-item">
					<div class="data-source-label">${t('data.local_temp')}</div>
					<div class="data-source-value">${details.local_temp?.toFixed(1) || 'N/A'}°C</div>
				</div>
				<div class="data-source-item">
					<div class="data-source-label">${t('data.local_precip')}</div>
					<div class="data-source-value">${details.local_prec?.toFixed(1) || 'N/A'}mm</div>
				</div>
			</div>
			<div class="data-source-formula">
				<span class="highlight">${t('data.local_model_only')}</span><br>
				(ARIMA+LSTM)
			</div>`;
	}
	
	return `
		<div class="card ${cls}" onclick="flipCard(this)" data-date="${item.date}">
			<div class="card-front">
				<div class="date">${item.date} ${icon}</div>
				<div class="temp">${item.temperature_c.toFixed(1)}°C <span style="color:var(--muted);font-size:12px">(↑${item.tmax?.toFixed?.(1)} ↓${item.tmin?.toFixed?.(1)})</span></div>
				<div class="meta">${lp}：${item.precipitation_mm.toFixed(1)} mm<br/>${lh}：${item.humidity.toFixed(0)}%　${lw}：${item.wind_speed_ms.toFixed(1)} m/s</div>
				<div class="flip-hint">点击翻转</div>
			</div>
			<div class="card-back">
				${backContent}
			</div>
		</div>
	`;
}

// 卡片点击功能 - 模态框版本
function flipCard(cardElement) {
	console.log('Card clicked, showing data source modal...'); // 调试信息
	
	// 防止重复点击
	if (cardElement.classList.contains('flipping')) {
		return;
	}
	
	cardElement.classList.add('flipping');
	
	// 显示数据来源模态框
	showDataSourceModal(cardElement);
	
	// 移除翻转中状态
	setTimeout(() => {
		cardElement.classList.remove('flipping');
	}, 400);
}

// 显示数据来源模态框
function showDataSourceModal(cardElement) {
	// 获取卡片的数据来源信息
	const cardData = getCardDataSource(cardElement);
	
	// 填充模态框内容
	const modalBody = document.getElementById('data-source-modal-body');
	modalBody.innerHTML = cardData;
	
	// 显示模态框
	const modal = document.getElementById('data-source-modal');
	modal.classList.add('show');
	
	// 阻止页面滚动
	document.body.style.overflow = 'hidden';
}

// 关闭数据来源模态框
function closeDataSourceModal() {
	const modal = document.getElementById('data-source-modal');
	modal.classList.remove('show');
	
	// 恢复页面滚动
	document.body.style.overflow = '';
}

// 获取卡片的数据来源信息
function getCardDataSource(cardElement) {
	// 从卡片的背面内容中提取数据
	const cardBack = cardElement.querySelector('.card-back');
	if (!cardBack) {
		return '<p>暂无数据来源信息</p>';
	}
	
	// 克隆背面内容并调整样式
	const content = cardBack.cloneNode(true);
	
	// 转换为模态框格式
	let html = '<div class="data-source-modal-grid">';
	
	// 提取数据项
	const dataItems = content.querySelectorAll('.data-source-item');
	dataItems.forEach(item => {
		const label = item.querySelector('.data-source-label')?.textContent || '';
		const value = item.querySelector('.data-source-value')?.textContent || '';
		html += `
			<div class="data-source-modal-item">
				<div class="data-source-modal-label">${label}</div>
				<div class="data-source-modal-value">${value}</div>
			</div>
		`;
	});
	
	html += '</div>';
	
	// 添加公式
	const formula = content.querySelector('.data-source-formula');
	if (formula) {
		html += `<div class="data-source-modal-formula">${formula.innerHTML}</div>`;
	}
	
	return html;
}

// 点击模态框背景关闭
document.addEventListener('DOMContentLoaded', function() {
	const modal = document.getElementById('data-source-modal');
	if (modal) {
		modal.addEventListener('click', function(e) {
			if (e.target === modal) {
				closeDataSourceModal();
			}
		});
	}
	
	// ESC键关闭模态框
	document.addEventListener('keydown', function(e) {
		if (e.key === 'Escape') {
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
		
		// 保存预报数据并更新背景
		window.currentForecastData = list;
		updateWeatherBackground();
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
	const chips = (x.reasons||[]).map(r=>`<span class="chip">${translateWeatherReason(r)}</span>`).join('');
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
		
		// 显示加载状态
		btnSend.disabled = true;
		btnSend.textContent = t('assistant.sending') || '发送中...';
		
		try{ 
			renderAdvice(await getJSON(`/api/nlp?q=${encodeURIComponent(raw)}&city=${encodeURIComponent(currentCity())}`)); 
		} catch(e){ 
			showText(t('tips.unknown')); 
		} finally {
			// 恢复按钮状态
			btnSend.disabled = false;
			btnSend.textContent = t('assistant.send');
		}
	});
}

async function refreshData(){
	applyI18n();
	showLoader();
	try{
		await renderForecast();
		await renderHistory();
		await renderExtremes();
	} finally {
		hideLoader();
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

// 显示加载动画
function showLoader(text = null) {
	const loader = document.getElementById('loader');
	const loaderText = document.querySelector('.loader-text');
	if (loader) {
		if (text) {
			loaderText.textContent = text;
		} else {
			const lang = document.getElementById('lang')?.value || 'zh';
			loaderText.textContent = lang === 'zh' ? '正在加载天气数据...' : 'Loading weather data...';
		}
		loader.style.display = 'flex';
	}
}

// 隐藏加载动画
function hideLoader() {
	const loader = document.getElementById('loader');
	if (loader) {
		loader.style.display = 'none';
	}
}

// 动态背景控制
class WeatherBackgroundController {
	constructor() {
		this.background = document.getElementById('weather-background');
		this.sunAnimation = document.getElementById('sun-animation');
		this.rainAnimation = document.getElementById('rain-animation');
		this.cloudsAnimation = document.getElementById('clouds-animation');
		this.currentWeather = 'sunny';
		this.rainDrops = [];
		this.clouds = [];
		this.init();
	}

	init() {
		// 初始化云朵
		this.createClouds();
		// 设置默认天气
		this.setWeather('sunny');
	}

	createClouds() {
		// 创建云朵
		for (let i = 0; i < 5; i++) {
			this.createCloud(i);
		}
	}

	createCloud(index) {
		const cloud = document.createElement('div');
		cloud.className = 'cloud';
		
		// 随机云朵大小和位置
		const size = 60 + Math.random() * 80;
		const top = 10 + Math.random() * 30;
		const duration = 20 + Math.random() * 30;
		const delay = Math.random() * 20;
		
		cloud.style.cssText = `
			width: ${size}px;
			height: ${size * 0.6}px;
			top: ${top}%;
			animation-duration: ${duration}s;
			animation-delay: -${delay}s;
		`;
		
		// 创建云朵的圆形部分
		const beforeSize = size * 0.4;
		const afterSize = size * 0.3;
		
		cloud.style.setProperty('--before-size', `${beforeSize}px`);
		cloud.style.setProperty('--after-size', `${afterSize}px`);
		
		cloud.style.setProperty('--before-left', `${size * 0.2}px`);
		cloud.style.setProperty('--before-top', `${size * 0.3}px`);
		cloud.style.setProperty('--after-left', `${size * 0.6}px`);
		cloud.style.setProperty('--after-top', `${size * 0.2}px`);
		
		this.cloudsAnimation.appendChild(cloud);
		this.clouds.push(cloud);
	}

	createRainDrops() {
		// 清除现有雨滴
		this.rainAnimation.innerHTML = '';
		this.rainDrops = [];
		
		// 创建新雨滴
		for (let i = 0; i < 100; i++) {
			const drop = document.createElement('div');
			drop.className = 'rain-drop';
			
			// 随机雨滴位置和速度
			const left = Math.random() * 100;
			const duration = 0.5 + Math.random() * 1;
			const delay = Math.random() * 2;
			
			drop.style.cssText = `
				left: ${left}%;
				animation-duration: ${duration}s;
				animation-delay: -${delay}s;
			`;
			
			this.rainAnimation.appendChild(drop);
			this.rainDrops.push(drop);
		}
	}

	setWeather(weather) {
		if (this.currentWeather === weather) return;
		
		this.currentWeather = weather;
		
		// 移除现有主题类
		this.background.classList.remove('sunny', 'rainy');
		
		// 添加新主题类
		this.background.classList.add(weather);
		
		// 控制动画元素
		if (weather === 'sunny') {
			this.sunAnimation.classList.add('show');
			this.rainAnimation.classList.remove('show');
			this.cloudsAnimation.classList.add('show');
		} else if (weather === 'rainy') {
			this.sunAnimation.classList.remove('show');
			this.rainAnimation.classList.add('show');
			this.cloudsAnimation.classList.add('show');
			this.createRainDrops();
		}
	}

	// 根据天气预报数据自动设置背景
	setWeatherFromForecast(forecastData) {
		if (!forecastData || forecastData.length === 0) return;
		
		// 分析未来几天的天气情况，使用更精确的判定标准
		let sunnyDays = 0;
		let rainyDays = 0;
		let totalPrecip = 0;
		
		forecastData.forEach(day => {
			const precip = parseFloat(day.precipitation_mm) || 0;
			totalPrecip += precip;
			
			// 降水阈值：0.5mm以下为晴天，0.5mm以上为雨天
			if (precip > 0.5) {
				rainyDays++;
			} else {
				sunnyDays++;
			}
		});
		
		// 计算平均降水量
		const avgPrecip = totalPrecip / forecastData.length;
		
		// 判定逻辑：
		// 1. 如果雨天数量 > 晴天数量，设为雨天
		// 2. 如果平均降水量 > 2mm，设为雨天
		// 3. 否则设为晴天
		let weatherType = 'sunny';
		
		if (rainyDays > sunnyDays || avgPrecip > 2) {
			weatherType = 'rainy';
		}
		
		console.log(`天气背景判定: 晴天${sunnyDays}天, 雨天${rainyDays}天, 平均降水${avgPrecip.toFixed(1)}mm -> ${weatherType}`);
		
		this.setWeather(weatherType);
	}
}

// 初始化动态背景控制器
let weatherBackgroundController;

// 在页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
	weatherBackgroundController = new WeatherBackgroundController();
});

// 在渲染预报后更新背景
function updateWeatherBackground() {
	if (weatherBackgroundController && window.currentForecastData) {
		weatherBackgroundController.setWeatherFromForecast(window.currentForecastData);
	}
}
