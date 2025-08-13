'use strict';

(function () {
  const STATE_KEY = 'tbs_state_v1';
  const NOW = () => Date.now();
  const SEC = 1000;
  const MIN = 60 * SEC;
  const HOUR = 60 * MIN;
  const DAY = 24 * HOUR;

  // Config Definitions
  const CONFIG = {
    clickBaseAtLevel: (level) => 0.5 * Math.pow(2, Math.max(0, level - 1)),
    clicksRequiredAtLevel: (level) => 100 * Math.pow(2, Math.max(0, level - 1)),
    giftCooldownMs: 10 * MIN,
    giftDailyMax: 5,
    adBoostDurationMs: 5 * MIN,
    adWindowDurationMs: 12 * HOUR,
    adBaseMultiplier: 5,
    adIncrementPerView: 2,
    offlineCapMs: 8 * HOUR,
    footballMatchIntervalMs: 5 * MIN,
    vadesizDailyRate: 0.001, // 0.1%/day
    bankStockMonthlyDividendRate: 0.01, // 1%/month
    forexUpdateIntervalMs: 10 * SEC,
    stockUpdateIntervalMs: 12 * SEC,
    prestigeB: 1_000_000, // TL
    prestigeMultiplierPerPoint: 0.05,
    companies: [
      { id: 'bakkal', name: 'Bakkal', baseIncomePerSec: 0.25, baseCost: 25, unlockLevel: 1, growthPerLevel: 0.15 },
      { id: 'kafe', name: 'Kafe', baseIncomePerSec: 1, baseCost: 120, unlockLevel: 3, growthPerLevel: 0.15 },
      { id: 'market', name: 'Market', baseIncomePerSec: 2, baseCost: 240, unlockLevel: 3, growthPerLevel: 0.15 },
      { id: 'restoran', name: 'Restoran', baseIncomePerSec: 4, baseCost: 600, unlockLevel: 5, growthPerLevel: 0.15 },
      { id: 'fabrika', name: 'Fabrika', baseIncomePerSec: 50, baseCost: 15_000, unlockLevel: 20, growthPerLevel: 0.14 },
      { id: 'holding', name: 'Holding', baseIncomePerSec: 200, baseCost: 60_000, unlockLevel: 30, growthPerLevel: 0.14 },
    ],
    marketItems: [
      { id: 'phone', name: 'Akıllı Telefon', cost: 2_500, effects: { clickMultiplierPct: 0.02 } },
      { id: 'laptop', name: 'Laptop', cost: 7_500, effects: { passiveMultiplierPct: 0.03 } },
      { id: 'watch', name: 'Lüks Saat', cost: 25_000, effects: { clickMultiplierPct: 0.03, passiveMultiplierPct: 0.02 } },
      { id: 'bike', name: 'Bisiklet', cost: 1_200, effects: { passiveMultiplierPct: 0.01 } },
      { id: 'car', name: 'Araba', cost: 85_000, effects: { passiveMultiplierPct: 0.05 } },
      { id: 'yacht', name: 'Yat', cost: 1_250_000, effects: { passiveMultiplierPct: 0.15, clickMultiplierPct: 0.05 } },
    ],
    research: [
      { id: 'r_click_1', name: 'Tıklama Verimliliği I', cost: 100_000, effects: { clickMultiplierPct: 0.10 } },
      { id: 'r_passive_1', name: 'Pasif Gelir I', cost: 150_000, effects: { passiveMultiplierPct: 0.10 } },
      { id: 'r_ads_1', name: 'Reklam Boost I', cost: 200_000, effects: { adBonusAdd: 1 } },
    ],
    football: {
      unlockLevel: 10,
      baseMatchIncome: 500,
      teamLevelMult: 0.12,
      stadiumMult: 0.20,
      sponsorMult: 0.10,
      playerQualityMult: 0.05,
    },
    forex: {
      assets: [
        { id: 'USD', name: 'USD', startPrice: 32.0 },
        { id: 'EUR', name: 'EUR', startPrice: 35.0 },
        { id: 'XAU', name: 'Gram Altın', startPrice: 2500.0 },
      ]
    },
    stock: { id: 'TURKBANK', name: 'Turkey Bank Hissesi', startPrice: 100.0 }
  };

  // State
  function defaultState() {
    return {
      createdAt: NOW(),
      lastSeenAt: NOW(),
      money: 0,
      lifetimeEarnings: 0,
      level: 1,
      clicksThisLevel: 0,
      ad: { views: 0, windowStart: 0, activeUntil: 0, bonusAddFromResearch: 0 },
      gift: { lastClaim: 0, claimsToday: 0, lastDayKey: dayKey(NOW()) },
      prestige: { points: 0, theoreticalGrantedBase: 0 },
      companies: {},
      football: { unlocked: false, lastMatchAt: 0, teamLevel: 0, stadiumLevel: 0, sponsorLevel: 0, playerQuality: 0 },
      bank: {
        vadesiz: 0,
        lastVadesizInterestDay: dayKey(NOW()),
        timeDeposits: [], // { id, amount, rateDaily, days, startAt }
        forex: {
          lastUpdate: 0,
          prices: {}, // id -> price
          holdings: {} // id -> amount
        },
        stock: { price: CONFIG.stock.startPrice, shares: 0, lastUpdate: 0, lastDividendAt: NOW() },
        loans: [] // { id, type: 'small'|'business', principal, rateDaily, termDays, startAt, lastAccruedDay }
      },
      market: { owned: {} },
      research: { owned: {} },
      ui: { currentTab: 'home' }
    };
  }

  function dayKey(ts) {
    const d = new Date(ts);
    return `${d.getFullYear()}-${d.getMonth()+1}-${d.getDate()}`;
  }

  let state = loadState();

  // Initialization helpers
  function ensureDerivedState() {
    // Initialize companies state
    for (const c of CONFIG.companies) {
      if (!state.companies[c.id]) state.companies[c.id] = { level: 0, unlocked: false };
      if (!state.companies[c.id].unlocked && state.level >= c.unlockLevel) state.companies[c.id].unlocked = true;
    }
    // Initialize forex
    for (const a of CONFIG.forex.assets) {
      if (state.bank.forex.prices[a.id] == null) state.bank.forex.prices[a.id] = a.startPrice;
      if (state.bank.forex.holdings[a.id] == null) state.bank.forex.holdings[a.id] = 0;
    }
    // Football unlock
    if (!state.football.unlocked && state.level >= CONFIG.football.unlockLevel) state.football.unlocked = true;
  }

  ensureDerivedState();
  applyOfflineProgress();
  saveState();

  // UI References
  const el = {
    balanceText: document.getElementById('balanceText'),
    levelText: document.getElementById('levelText'),
    perSecText: document.getElementById('perSecText'),
    clickButton: document.getElementById('clickButton'),
    levelProgress: document.getElementById('levelProgress'),
    levelInfo: document.getElementById('levelInfo'),
    btnGift: document.getElementById('btnGift'),
    giftCountdown: document.getElementById('giftCountdown'),
    btnAd: document.getElementById('btnAd'),
    adCountdown: document.getElementById('adCountdown'),
    prestigeText: document.getElementById('prestigeText'),
    companiesList: document.getElementById('companiesList'),
    footballCard: document.getElementById('footballCard'),
    demandBalance: document.getElementById('demandBalance'),
    demandAmount: document.getElementById('demandAmount'),
    btnDeposit: document.getElementById('btnDeposit'),
    btnWithdraw: document.getElementById('btnWithdraw'),
    demandInfo: document.getElementById('demandInfo'),
    tdAmount: document.getElementById('tdAmount'),
    tdDays: document.getElementById('tdDays'),
    btnOpenTD: document.getElementById('btnOpenTD'),
    tdList: document.getElementById('tdList'),
    forexList: document.getElementById('forexList'),
    stockCard: document.getElementById('stockCard'),
    marketList: document.getElementById('marketList'),
    researchList: document.getElementById('researchList'),
    navButtons: document.querySelectorAll('.nav-btn'),
    tabs: {
      home: document.getElementById('tab-home'),
      companies: document.getElementById('tab-companies'),
      invest: document.getElementById('tab-invest'),
      market: document.getElementById('tab-market'),
      research: document.getElementById('tab-research')
    },
    btnSettings: document.getElementById('btnSettings'),
    settingsModal: document.getElementById('settingsModal'),
    btnCloseSettings: document.getElementById('btnCloseSettings'),
    btnSave: document.getElementById('btnSave'),
    btnHardReset: document.getElementById('btnHardReset'),
    btnPrestige: document.getElementById('btnPrestige'),
    prestigeInfo: document.getElementById('prestigeInfo'),
    btnLoanSmall: document.getElementById('btnLoanSmall'),
    btnLoanBusiness: document.getElementById('btnLoanBusiness'),
    loanList: document.getElementById('loanList')
  };

  // Event Listeners
  el.clickButton.addEventListener('click', onClickEarn);
  el.btnGift.addEventListener('click', onGiftClaim);
  el.btnAd.addEventListener('click', onWatchAd);

  el.navButtons.forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
  });

  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') saveState();
  });

  window.addEventListener('beforeunload', () => saveState());

  el.btnDeposit.addEventListener('click', () => {
    const amount = parseNumber(el.demandAmount.value);
    if (amount > 0 && state.money >= amount) {
      addMoney(-amount);
      state.bank.vadesiz += amount;
      uiToast('Vadesize yatırıldı');
      renderBank();
    }
  });

  el.btnWithdraw.addEventListener('click', () => {
    const amount = parseNumber(el.demandAmount.value);
    if (amount > 0 && state.bank.vadesiz >= amount) {
      state.bank.vadesiz -= amount;
      addMoney(amount);
      uiToast('Vadesizden çekildi');
      renderBank();
    }
  });

  el.btnOpenTD.addEventListener('click', () => {
    const amount = parseNumber(el.tdAmount.value);
    const days = Math.max(1, Math.min(30, Math.floor(parseNumber(el.tdDays.value))));
    if (amount > 0 && state.money >= amount) {
      const rateDaily = calcTimeDepositDailyRate();
      const dep = { id: 'td_' + Math.random().toString(36).slice(2), amount, rateDaily, days, startAt: NOW() };
      addMoney(-amount);
      state.bank.timeDeposits.push(dep);
      uiToast(`Vadeli ${days} gün açıldı`);
      renderBank();
    }
  });

  // Loans
  el.btnLoanSmall.addEventListener('click', () => {
    openLoan('small');
  });
  el.btnLoanBusiness.addEventListener('click', () => {
    openLoan('business');
  });

  el.btnSettings.addEventListener('click', () => showSettings(true));
  el.btnCloseSettings.addEventListener('click', () => showSettings(false));
  el.btnSave.addEventListener('click', () => { saveState(true); uiToast('Kaydedildi'); });
  el.btnHardReset.addEventListener('click', () => {
    if (confirm('Tüm ilerleme sıfırlansın mı? Prestij puanları HARİÇ her şey silinir.')) {
      const prestige = state.prestige;
      state = defaultState();
      state.prestige = prestige;
      ensureDerivedState();
      saveState(true);
      fullRender();
      uiToast('Oyun sıfırlandı');
    }
  });

  el.btnPrestige.addEventListener('click', () => {
    const pending = computePrestigePendingPoints();
    if (pending <= 0) {
      uiToast('Prestij için yeterli birikim yok');
      return;
    }
    if (confirm(`Prestij yapmak istiyor musun? Kazanılacak puan: ${pending}`)) {
      applyPrestige(pending);
      showSettings(false);
      uiToast(`Prestij yapıldı! +${pending} puan`);
    }
  });

  // Core Logic
  function onClickEarn() {
    resetDailyGiftIfNeeded();
    resetAdWindowIfNeeded();
    const adMult = getAdMultiplier();
    const clickBase = CONFIG.clickBaseAtLevel(state.level);
    const value = clickBase * getGlobalClickMultiplier() * adMult;
    addMoney(value);
    state.clicksThisLevel += 1;
    maybeLevelUp();
    renderHeader();
    renderLevel();
  }

  function maybeLevelUp() {
    const req = CONFIG.clicksRequiredAtLevel(state.level);
    if (state.clicksThisLevel >= req) {
      state.level += 1;
      state.clicksThisLevel = 0;
      ensureDerivedState();
      uiToast(`Seviye ${state.level}`);
      renderAllLists();
    }
  }

  function onGiftClaim() {
    resetDailyGiftIfNeeded();
    const availableIn = giftAvailableInMs();
    if (state.gift.claimsToday >= CONFIG.giftDailyMax) return;
    if (availableIn > 0) return;
    const amount = state.level * 100 * getGlobalPassiveMultiplier();
    addMoney(amount);
    state.gift.lastClaim = NOW();
    state.gift.claimsToday += 1;
    renderGift();
    renderHeader();
  }

  function onWatchAd() {
    resetAdWindowIfNeeded();
    const now = NOW();
    if (state.ad.windowStart === 0 || now - state.ad.windowStart > CONFIG.adWindowDurationMs) {
      state.ad.windowStart = now;
      state.ad.views = 0;
    }
    state.ad.views += 1;
    const base = CONFIG.adBaseMultiplier + CONFIG.adIncrementPerView * (state.ad.views - 1);
    const researchAdd = state.ad.bonusAddFromResearch;
    state.ad.activeUntil = now + CONFIG.adBoostDurationMs;
    el.btnAd.textContent = `Reklam İzle ×${(base + researchAdd).toFixed(0)}`;
    renderAd();
  }

  function resetDailyGiftIfNeeded() {
    const key = dayKey(NOW());
    if (state.gift.lastDayKey !== key) {
      state.gift.lastDayKey = key;
      state.gift.claimsToday = 0;
    }
  }

  function resetAdWindowIfNeeded() {
    const now = NOW();
    if (state.ad.windowStart === 0) return;
    if (now - state.ad.windowStart > CONFIG.adWindowDurationMs) {
      state.ad.windowStart = now;
      state.ad.views = 0;
    }
  }

  function giftAvailableInMs() {
    if (state.gift.lastClaim === 0) return 0;
    const diff = CONFIG.giftCooldownMs - (NOW() - state.gift.lastClaim);
    return Math.max(0, diff);
  }

  function getAdMultiplier() {
    const now = NOW();
    if (now < state.ad.activeUntil) {
      const base = CONFIG.adBaseMultiplier + CONFIG.adIncrementPerView * Math.max(0, state.ad.views - 1);
      return base + state.ad.bonusAddFromResearch;
    }
    return 1;
  }

  function getPrestigeMultiplier() {
    return 1 + (state.prestige.points * CONFIG.prestigeMultiplierPerPoint);
  }

  function getGlobalClickMultiplier() {
    let mult = getPrestigeMultiplier();
    // Market
    mult *= (1 + sumOwnedEffects('clickMultiplierPct'));
    // Research
    mult *= (1 + sumOwnedResearchEffects('clickMultiplierPct'));
    return mult;
  }

  function getGlobalPassiveMultiplier() {
    let mult = getPrestigeMultiplier();
    mult *= (1 + sumOwnedEffects('passiveMultiplierPct'));
    mult *= (1 + sumOwnedResearchEffects('passiveMultiplierPct'));
    return mult;
  }

  function sumOwnedEffects(key) {
    let sum = 0;
    for (const item of CONFIG.marketItems) {
      if (state.market.owned[item.id] && item.effects && item.effects[key]) sum += item.effects[key];
    }
    return sum;
  }

  function sumOwnedResearchEffects(key) {
    let sum = 0;
    for (const r of CONFIG.research) {
      if (state.research.owned[r.id] && r.effects && r.effects[key]) sum += r.effects[key];
    }
    return sum;
  }

  function addMoney(amount) {
    state.money += amount;
    if (amount > 0) state.lifetimeEarnings += amount;
  }

  function formatMoney(value) {
    const sign = value < 0 ? '-' : '';
    const n = Math.abs(value);
    const suffixes = [ {v: 1e12, s: 'T'}, {v: 1e9, s: 'B'}, {v: 1e6, s: 'M'}, {v: 1e3, s: 'K'} ];
    for (const k of suffixes) {
      if (n >= k.v) return `${sign}₺${(n / k.v).toFixed(2)}${k.s}`;
    }
    return `${sign}₺${n.toFixed(2)}`;
  }

  function parseNumber(v) {
    if (!v) return 0;
    const num = Number(v);
    return isFinite(num) ? num : 0;
  }

  function companyIncomePerSec(comp, stateComp) {
    const level = stateComp.level;
    if (level <= 0) return 0;
    const base = comp.baseIncomePerSec;
    const growth = 1 + comp.growthPerLevel * level;
    return base * growth * getGlobalPassiveMultiplier();
  }

  function totalPassiveIncomePerSec() {
    let sum = 0;
    for (const comp of CONFIG.companies) {
      const st = state.companies[comp.id];
      sum += companyIncomePerSec(comp, st);
    }
    // Market and Research multipliers are already inside companyIncomePerSec via getGlobalPassiveMultiplier
    // Add football passive? Matches are discrete; not per sec.
    return sum;
  }

  function upgradeCost(comp, level) {
    // Geometric growth cost
    const base = comp.baseCost;
    const factor = 1.15;
    return Math.floor(base * Math.pow(factor, level));
  }

  function renderHeader() {
    el.balanceText.textContent = formatMoney(state.money);
    el.levelText.textContent = `Lv ${state.level}`;
    el.perSecText.textContent = formatMoney(totalPassiveIncomePerSec()).replace('₺', '');
    el.prestigeText.textContent = `${state.prestige.points}`;
    // Click button label
    el.clickButton.textContent = `Tıkla ${formatMoney(CONFIG.clickBaseAtLevel(state.level) * getGlobalClickMultiplier())}`;
  }

  function renderLevel() {
    const req = CONFIG.clicksRequiredAtLevel(state.level);
    const progress = Math.min(100, (state.clicksThisLevel / req) * 100);
    el.levelProgress.style.width = `${progress}%`;
    el.levelInfo.textContent = `Seviye ${state.level}: ${state.clicksThisLevel} / ${req} tıklama`;
  }

  function renderGift() {
    resetDailyGiftIfNeeded();
    const availableIn = giftAvailableInMs();
    const canClaim = state.gift.claimsToday < CONFIG.giftDailyMax && availableIn === 0;
    el.btnGift.disabled = !canClaim;
    if (state.gift.claimsToday >= CONFIG.giftDailyMax) {
      el.giftCountdown.textContent = 'Günlük limit doldu';
    } else if (availableIn > 0) {
      el.giftCountdown.textContent = `Sonraki: ${formatDuration(availableIn)}`;
    } else {
      el.giftCountdown.textContent = 'Hazır';
    }
  }

  function renderAd() {
    resetAdWindowIfNeeded();
    const now = NOW();
    const active = now < state.ad.activeUntil;
    const base = CONFIG.adBaseMultiplier + CONFIG.adIncrementPerView * Math.max(0, state.ad.views - 1);
    const label = `Reklam İzle ×${(base + state.ad.bonusAddFromResearch).toFixed(0)}`;
    el.btnAd.textContent = label;
    el.adCountdown.textContent = active ? `Aktif: ${formatDuration(state.ad.activeUntil - now)}` : 'Pasif';
  }

  function renderCompanies() {
    const container = el.companiesList;
    container.innerHTML = '';

    for (const comp of CONFIG.companies) {
      const st = state.companies[comp.id];
      const card = document.createElement('div');
      card.className = 'card';
      const income = companyIncomePerSec(comp, st);
      const cost = upgradeCost(comp, st.level);
      const canUnlock = !st.unlocked && state.level >= comp.unlockLevel;

      card.innerHTML = `
        <h4>${comp.name} ${st.level > 0 ? '(Lv ' + st.level + ')' : ''}</h4>
        <div class="muted">Gelir: ${formatMoney(income)}/sn</div>
        <div class="row">
          <div class="muted">${st.unlocked ? 'Yükselt' : (canUnlock ? 'Kilidi Aç' : 'Lv ' + comp.unlockLevel + ' gereklidir')}</div>
          <button class="primary small" ${(!st.unlocked && !canUnlock) ? 'disabled' : ''} data-action="upgrade" data-id="${comp.id}">${st.unlocked ? '₺ ' + formatMoney(cost).replace('₺','') : '₺ ' + formatMoney(comp.baseCost).replace('₺','')}</button>
        </div>
      `;

      card.querySelector('button[data-action="upgrade"]').addEventListener('click', () => {
        if (!st.unlocked) {
          if (state.money >= comp.baseCost && canUnlock) {
            addMoney(-comp.baseCost);
            st.unlocked = true;
            st.level = 1;
            renderCompanies();
            renderHeader();
          }
          return;
        }
        const costNow = upgradeCost(comp, st.level);
        if (state.money >= costNow) {
          addMoney(-costNow);
          st.level += 1;
          renderCompanies();
          renderHeader();
        }
      });

      container.appendChild(card);
    }
  }

  function computeFootballMatchIncome() {
    if (!state.football.unlocked) return 0;
    const base = CONFIG.football.baseMatchIncome;
    const t = state.football.teamLevel;
    const s = state.football.stadiumLevel;
    const sp = state.football.sponsorLevel;
    const q = state.football.playerQuality;
    const mult = (1 + CONFIG.football.teamLevelMult * t) * (1 + CONFIG.football.stadiumMult * s) * (1 + CONFIG.football.sponsorMult * sp) * (1 + CONFIG.football.playerQualityMult * q) * getGlobalPassiveMultiplier();
    return base * mult;
  }

  function renderFootball() {
    const container = el.footballCard;
    container.innerHTML = '';
    const card = document.createElement('div');
    card.className = 'card';
    if (!state.football.unlocked) {
      card.innerHTML = `<div>Lv ${CONFIG.football.unlockLevel} seviyede açılır.</div>`;
      container.appendChild(card);
      return;
    }
    const nextInMs = nextFootballInMs();
    const income = computeFootballMatchIncome();
    card.innerHTML = `
      <h4>Futbol Kulübü</h4>
      <div class="muted">Maç başı gelir: ${formatMoney(income)}</div>
      <div class="muted">Sonraki maç: ${formatDuration(nextInMs)}</div>
      <div class="row">
        <button class="secondary small" data-action="team">Takım +1</button>
        <button class="secondary small" data-action="stadium">Stadyum +1</button>
        <button class="secondary small" data-action="sponsor">Sponsorluk +1</button>
        <button class="secondary small" data-action="transfer">Transfer (+kalite)</button>
      </div>
      <div class="muted">Seviyeler: Takım ${state.football.teamLevel}, Stadyum ${state.football.stadiumLevel}, Sponsor ${state.football.sponsorLevel}, Kalite ${state.football.playerQuality}</div>
    `;

    const costs = {
      team: 10_000 * Math.pow(1.25, state.football.teamLevel),
      stadium: 15_000 * Math.pow(1.25, state.football.stadiumLevel),
      sponsor: 12_000 * Math.pow(1.25, state.football.sponsorLevel),
      transfer: 8_000 * Math.pow(1.35, state.football.playerQuality)
    };

    card.querySelector('[data-action="team"]').textContent = `Takım +1 (₺${formatMoney(costs.team).replace('₺','')})`;
    card.querySelector('[data-action="stadium"]').textContent = `Stadyum +1 (₺${formatMoney(costs.stadium).replace('₺','')})`;
    card.querySelector('[data-action="sponsor"]').textContent = `Sponsor +1 (₺${formatMoney(costs.sponsor).replace('₺','')})`;
    card.querySelector('[data-action="transfer"]').textContent = `Transfer (₺${formatMoney(costs.transfer).replace('₺','')})`;

    card.querySelector('[data-action="team"]').addEventListener('click', () => {
      if (state.money >= costs.team) { addMoney(-costs.team); state.football.teamLevel += 1; renderFootball(); renderHeader(); }
    });
    card.querySelector('[data-action="stadium"]').addEventListener('click', () => {
      if (state.money >= costs.stadium) { addMoney(-costs.stadium); state.football.stadiumLevel += 1; renderFootball(); renderHeader(); }
    });
    card.querySelector('[data-action="sponsor"]').addEventListener('click', () => {
      if (state.money >= costs.sponsor) { addMoney(-costs.sponsor); state.football.sponsorLevel += 1; renderFootball(); renderHeader(); }
    });
    card.querySelector('[data-action="transfer"]').addEventListener('click', () => {
      if (state.money >= costs.transfer) { addMoney(-costs.transfer); state.football.playerQuality += 1; renderFootball(); renderHeader(); }
    });

    container.appendChild(card);
  }

  function nextFootballInMs() {
    const last = state.football.lastMatchAt || 0;
    const since = NOW() - last;
    const left = CONFIG.footballMatchIntervalMs - (since % CONFIG.footballMatchIntervalMs);
    return Math.max(0, left);
  }

  function renderBank() {
    el.demandBalance.textContent = formatMoney(state.bank.vadesiz);
    el.demandInfo.textContent = `Günlük faiz oranı: ${(CONFIG.vadesizDailyRate * 100).toFixed(2)}%`; 

    // Loans render first to keep visible
    renderLoans();

    // TD list
    el.tdList.innerHTML = '';
    for (const dep of state.bank.timeDeposits) {
      const elapsedDays = Math.floor((NOW() - dep.startAt) / DAY);
      const accrued = dep.amount * dep.rateDaily * Math.min(elapsedDays, dep.days);
      const matured = elapsedDays >= dep.days;
      const card = document.createElement('div');
      card.className = 'card';
      card.innerHTML = `
        <h4>Vadeli: ${dep.days} gün</h4>
        <div class="muted">Tutar: ${formatMoney(dep.amount)} | Faiz: ${(dep.rateDaily*100).toFixed(2)}%/gün</div>
        <div class="muted">Birikmiş faiz: ${formatMoney(accrued)} ${matured ? '(Vade doldu)' : ''}</div>
        <div class="row">
          <button class="primary small" data-action="withdraw">${matured ? 'Çek (Tam)' : 'Erken Çek (-%50 faiz)'}</button>
        </div>
      `;
      card.querySelector('[data-action="withdraw"]').addEventListener('click', () => {
        if (matured) {
          addMoney(dep.amount + accrued);
        } else {
          addMoney(dep.amount + (accrued * 0.5));
        }
        // remove deposit
        state.bank.timeDeposits = state.bank.timeDeposits.filter(d => d !== dep);
        renderBank();
        renderHeader();
      });
      el.tdList.appendChild(card);
    }

    // Forex list
    el.forexList.innerHTML = '';
    for (const asset of CONFIG.forex.assets) {
      const price = state.bank.forex.prices[asset.id];
      const amount = state.bank.forex.holdings[asset.id];
      const card = document.createElement('div');
      card.className = 'card';
      card.innerHTML = `
        <h4>${asset.name}</h4>
        <div class="muted">Fiyat: ₺${price.toFixed(2)} | Elde: ${amount.toFixed(3)}</div>
        <div class="row gap">
          <input data-field="amount" type="number" inputmode="decimal" placeholder="Miktar" />
          <button class="primary small" data-action="buy">Al</button>
          <button class="secondary small" data-action="sell">Sat</button>
        </div>
      `;
      const input = card.querySelector('[data-field="amount"]');
      card.querySelector('[data-action="buy"]').addEventListener('click', () => {
        const qty = parseNumber(input.value);
        const cost = qty * price;
        if (qty > 0 && state.money >= cost) {
          addMoney(-cost);
          state.bank.forex.holdings[asset.id] += qty;
          renderBank();
          renderHeader();
        }
      });
      card.querySelector('[data-action="sell"]').addEventListener('click', () => {
        const qty = parseNumber(input.value);
        if (qty > 0 && state.bank.forex.holdings[asset.id] >= qty) {
          state.bank.forex.holdings[asset.id] -= qty;
          addMoney(qty * price);
          renderBank();
          renderHeader();
        }
      });
      el.forexList.appendChild(card);
    }

    // Stock card
    el.stockCard.innerHTML = '';
    const scard = document.createElement('div');
    scard.className = 'card';
    const sp = state.bank.stock.price;
    const sh = state.bank.stock.shares;
    scard.innerHTML = `
      <h4>${CONFIG.stock.name}</h4>
      <div class="muted">Fiyat: ₺${sp.toFixed(2)} | Lot: ${sh.toFixed(2)}</div>
      <div class="row gap">
        <input data-field="shares" type="number" inputmode="decimal" placeholder="Lot" />
        <button class="primary small" data-action="buy">Al</button>
        <button class="secondary small" data-action="sell">Sat</button>
      </div>
    `;
    const inShares = scard.querySelector('[data-field="shares"]');
    scard.querySelector('[data-action="buy"]').addEventListener('click', () => {
      const qty = parseNumber(inShares.value);
      const cost = qty * state.bank.stock.price;
      if (qty > 0 && state.money >= cost) {
        addMoney(-cost);
        state.bank.stock.shares += qty;
        renderBank();
        renderHeader();
      }
    });
    scard.querySelector('[data-action="sell"]').addEventListener('click', () => {
      const qty = parseNumber(inShares.value);
      if (qty > 0 && state.bank.stock.shares >= qty) {
        state.bank.stock.shares -= qty;
        addMoney(qty * state.bank.stock.price);
        renderBank();
        renderHeader();
      }
    });
    el.stockCard.appendChild(scard);
  }

  function renderLoans() {
    el.loanList.innerHTML = '';
    for (const loan of state.bank.loans) {
      const elapsedDays = Math.floor((NOW() - loan.startAt) / DAY);
      const accrued = accrueLoanInterestPreview(loan);
      const remainingDays = Math.max(0, loan.termDays - elapsedDays);
      const card = document.createElement('div');
      card.className = 'card';
      card.innerHTML = `
        <h4>${loan.type === 'small' ? 'İhtiyaç Kredisi' : 'İşletme Kredisi'}</h4>
        <div class="muted">Anapara: ${formatMoney(loan.principal)} | Faiz: ${(loan.rateDaily*100).toFixed(2)}%/gün | Kalan gün: ${remainingDays}</div>
        <div class="muted">Ödenecek toplam: ${formatMoney(loan.principal + accrued)}</div>
        <div class="row">
          <button class="danger small" data-action="repay">Geri Öde</button>
        </div>
      `;
      card.querySelector('[data-action="repay"]').addEventListener('click', () => {
        // Accrue to today and repay if possible
        accrueLoanInterest(loan);
        const due = loan.principal;
        if (state.money >= due) {
          addMoney(-due);
          state.bank.loans = state.bank.loans.filter(l => l !== loan);
          uiToast('Kredi kapatıldı');
        } else {
          uiToast('Yetersiz bakiye');
        }
        renderBank();
        renderHeader();
      });
      el.loanList.appendChild(card);
    }
  }

  function openLoan(type) {
    // Determine principal, daily rate, term
    const isSmall = type === 'small';
    const principal = isSmall ? 1_500 : 25_000;
    const rateDaily = isSmall ? 0.01 : 0.006; // 1% vs 0.6%/day
    const termDays = isSmall ? 7 : 30;
    const loan = { id: 'ln_' + Math.random().toString(36).slice(2), type, principal, rateDaily, termDays, startAt: NOW(), lastAccruedDay: dayKey(NOW()) };
    state.bank.loans.push(loan);
    addMoney(principal);
    uiToast('Kredi kullanıldı');
    renderBank();
    renderHeader();
  }

  function accrueLoanInterestPreview(loan) {
    // multiplicative daily interest on principal
    const elapsedDays = Math.max(0, daysBetween(loan.lastAccruedDay, dayKey(NOW())));
    const factor = Math.pow(1 + loan.rateDaily, elapsedDays) - 1;
    return loan.principal * factor;
  }

  function accrueLoanInterest(loan) {
    // apply interest onto principal day by day until today
    let last = loan.lastAccruedDay;
    const today = dayKey(NOW());
    while (last !== today) {
      // increment date by 1
      const d = new Date(last);
      const next = new Date(d.getFullYear(), d.getMonth(), d.getDate() + 1);
      loan.principal *= (1 + loan.rateDaily);
      last = dayKey(next.getTime());
    }
    loan.lastAccruedDay = today;
  }

  function daysBetween(d1, d2) {
    const a = new Date(d1);
    const b = new Date(d2);
    const diff = Math.round((b - a) / DAY);
    return Math.max(0, diff);
  }

  function renderMarket() {
    el.marketList.innerHTML = '';
    for (const item of CONFIG.marketItems) {
      const owned = !!state.market.owned[item.id];
      const card = document.createElement('div');
      card.className = 'card';
      const effects = [];
      if (item.effects.clickMultiplierPct) effects.push(`Tıklama +${(item.effects.clickMultiplierPct*100).toFixed(0)}%`);
      if (item.effects.passiveMultiplierPct) effects.push(`Pasif +${(item.effects.passiveMultiplierPct*100).toFixed(0)}%`);
      card.innerHTML = `
        <h4>${item.name}</h4>
        <div class="muted">${effects.join(' • ') || 'Bonus'}</div>
        <div class="row">
          <div class="muted">${owned ? 'Satın alındı' : '₺ ' + formatMoney(item.cost).replace('₺','')}</div>
          <button class="primary small" ${owned ? 'disabled' : ''} data-id="${item.id}">${owned ? 'Sahip' : 'Satın Al'}</button>
        </div>
      `;
      if (!owned) {
        card.querySelector('button').addEventListener('click', () => {
          if (state.money >= item.cost) {
            addMoney(-item.cost);
            state.market.owned[item.id] = true;
            if (item.effects.adBonusAdd) state.ad.bonusAddFromResearch += item.effects.adBonusAdd;
            renderMarket();
            renderHeader();
          }
        });
      }
      el.marketList.appendChild(card);
    }
  }

  function renderResearch() {
    el.researchList.innerHTML = '';
    for (const r of CONFIG.research) {
      const owned = !!state.research.owned[r.id];
      const card = document.createElement('div');
      card.className = 'card';
      const effects = [];
      if (r.effects.clickMultiplierPct) effects.push(`Tıklama +${(r.effects.clickMultiplierPct*100).toFixed(0)}%`);
      if (r.effects.passiveMultiplierPct) effects.push(`Pasif +${(r.effects.passiveMultiplierPct*100).toFixed(0)}%`);
      if (r.effects.adBonusAdd) effects.push(`Reklam +${r.effects.adBonusAdd} ek çarpan`);
      card.innerHTML = `
        <h4>${r.name}</h4>
        <div class="muted">${effects.join(' • ')}</div>
        <div class="row">
          <div class="muted">${owned ? 'Araştırıldı' : '₺ ' + formatMoney(r.cost).replace('₺','')}</div>
          <button class="primary small" ${owned ? 'disabled' : ''} data-id="${r.id}">${owned ? 'Tamam' : 'Araştır'}</button>
        </div>
      `;
      if (!owned) {
        card.querySelector('button').addEventListener('click', () => {
          if (state.money >= r.cost) {
            addMoney(-r.cost);
            state.research.owned[r.id] = true;
            if (r.effects.adBonusAdd) state.ad.bonusAddFromResearch += r.effects.adBonusAdd;
            renderResearch();
            renderHeader();
            renderAd();
          }
        });
      }
      el.researchList.appendChild(card);
    }
  }

  function switchTab(tabKey) {
    for (const [k, node] of Object.entries(el.tabs)) {
      node.classList.toggle('active', k === tabKey);
    }
    el.navButtons.forEach(btn => btn.classList.toggle('active', btn.dataset.tab === tabKey));
    state.ui.currentTab = tabKey;
    if (tabKey === 'companies') renderCompanies();
    if (tabKey === 'invest') renderBank();
    if (tabKey === 'market') renderMarket();
    if (tabKey === 'research') renderResearch();
  }

  function formatDuration(ms) {
    ms = Math.max(0, ms);
    const s = Math.floor(ms / 1000);
    const m = Math.floor(s / 60);
    const h = Math.floor(m / 60);
    const s2 = s % 60;
    const m2 = m % 60;
    if (h > 0) return `${h}s ${m2}d`;
    if (m > 0) return `${m}d ${s2}s`;
    return `${s}s`;
  }

  function uiToast(msg) {
    // Simple toast via alert-like fade (minimal implementation)
    const t = document.createElement('div');
    t.textContent = msg;
    t.style.position = 'fixed';
    t.style.left = '50%';
    t.style.bottom = '80px';
    t.style.transform = 'translateX(-50%)';
    t.style.background = '#141e30';
    t.style.color = '#fff';
    t.style.padding = '10px 14px';
    t.style.borderRadius = '10px';
    t.style.boxShadow = '0 6px 16px rgba(0,0,0,0.3)';
    t.style.zIndex = '9999';
    document.body.appendChild(t);
    setTimeout(() => { t.style.opacity = '0'; t.style.transition = 'opacity .4s'; }, 1300);
    setTimeout(() => t.remove(), 1800);
  }

  function showSettings(show) {
    if (show) {
      const pending = computePrestigePendingPoints();
      el.prestigeInfo.textContent = `Potansiyel prestij puanı: ${pending} | Çarpan: x${(1 + state.prestige.points * CONFIG.prestigeMultiplierPerPoint).toFixed(2)}`;
    }
    el.settingsModal.classList.toggle('hidden', !show);
  }

  function computePrestigePendingPoints() {
    const theoretical = Math.floor(Math.sqrt(state.lifetimeEarnings / CONFIG.prestigeB));
    const pending = theoretical - (state.prestige.theoreticalGrantedBase || 0);
    return Math.max(0, pending);
  }

  function applyPrestige(pointsEarned) {
    state.prestige.points += pointsEarned;
    state.prestige.theoreticalGrantedBase += pointsEarned;
    // Reset most state
    const keep = { prestige: state.prestige };
    state = defaultState();
    state.prestige = keep.prestige;
    ensureDerivedState();
    saveState(true);
    fullRender();
  }

  function calcTimeDepositDailyRate() {
    const base = 0.001; // 0.1%/gün
    const levelBonus = Math.min(0.002, state.level * 0.00002);
    const prestigeBonus = Math.min(0.003, state.prestige.points * 0.0005);
    return base + levelBonus + prestigeBonus;
  }

  function accrueVadesizInterestIfNeeded() {
    const today = dayKey(NOW());
    let last = state.bank.lastVadesizInterestDay || dayKey(state.createdAt);
    while (last !== today) {
      // increment last by one day
      const d = new Date(last);
      const next = new Date(d.getFullYear(), d.getMonth(), d.getDate() + 1);
      const lastMs = next.getTime();
      last = dayKey(lastMs);
      const interest = state.bank.vadesiz * CONFIG.vadesizDailyRate;
      state.bank.vadesiz += interest;
    }
    state.bank.lastVadesizInterestDay = today;
  }

  function updateForexPrices(dtMs) {
    const meanRevert = 0.0005; // toward start price
    for (const a of CONFIG.forex.assets) {
      const p = state.bank.forex.prices[a.id];
      const dt = dtMs / (10 * 1000);
      const noise = (Math.random() - 0.5) * 0.006 * dt; // +-0.3% per 10s
      const reversion = (a.startPrice - p) * meanRevert * dt;
      const next = Math.max(0.01, p * (1 + noise) + reversion);
      state.bank.forex.prices[a.id] = next;
    }
  }

  function updateStockPrice(dtMs) {
    const p = state.bank.stock.price;
    const dt = dtMs / (12 * 1000);
    const noise = (Math.random() - 0.5) * 0.01 * dt; // +-0.5% per 12s
    const drift = 0.0002 * dt;
    let next = Math.max(1, p * (1 + drift + noise));
    state.bank.stock.price = next;
  }

  function maybePayStockDividend() {
    const now = NOW();
    const last = state.bank.stock.lastDividendAt || now;
    if (now - last >= 30 * DAY) {
      const months = Math.floor((now - last) / (30 * DAY));
      const perShare = state.bank.stock.price * CONFIG.bankStockMonthlyDividendRate;
      const total = perShare * state.bank.stock.shares * months;
      if (total > 0) addMoney(total);
      state.bank.stock.lastDividendAt = last + months * 30 * DAY;
    }
  }

  function applyOfflineProgress() {
    ensureDerivedState();
    const now = NOW();
    const elapsed = Math.min(CONFIG.offlineCapMs, now - (state.lastSeenAt || now));
    if (elapsed <= 0) return;
    // passive income
    const perSec = totalPassiveIncomePerSec();
    const passive = perSec * (elapsed / 1000);
    addMoney(passive);
    // football matches
    const matches = Math.floor(elapsed / CONFIG.footballMatchIntervalMs);
    const perMatch = computeFootballMatchIncome();
    addMoney(matches * perMatch);
    // vadesiz interest over days
    accrueVadesizInterestIfNeeded();
    // time deposit interest is represented at withdrawal only (accrual displayed based on time)
    // forex/stock simulate price drift
    updateForexPrices(elapsed);
    updateStockPrice(elapsed);
    maybePayStockDividend();
    // Also accrue loan interests to keep previews fresh
    for (const loan of state.bank.loans) {
      // passive preview only, do not mutate principal every second; accrue on repay or once per day
    }
    state.lastSeenAt = now;
  }

  function saveState(force) {
    try {
      localStorage.setItem(STATE_KEY, JSON.stringify(state));
      if (force) state.lastSavedAt = NOW();
    } catch (e) {
      // ignore
    }
  }

  function loadState() {
    try {
      const raw = localStorage.getItem(STATE_KEY);
      if (!raw) return defaultState();
      const parsed = JSON.parse(raw);
      return Object.assign(defaultState(), parsed);
    } catch (e) {
      return defaultState();
    }
  }

  function fullRender() {
    renderHeader();
    renderLevel();
    renderGift();
    renderAd();
    renderCompanies();
    renderFootball();
    renderBank();
    renderMarket();
    renderResearch();
  }

  function renderAllLists() {
    renderCompanies();
    renderFootball();
    renderMarket();
    renderResearch();
  }

  // Timers
  let lastTick = NOW();
  setInterval(() => {
    const now = NOW();
    const dt = now - lastTick;
    lastTick = now;

    // Passive income per second
    const perSec = totalPassiveIncomePerSec();
    addMoney(perSec);

    // Football periodic matches
    if (state.football.unlocked) {
      if (!state.football.lastMatchAt) state.football.lastMatchAt = now;
      if (now - state.football.lastMatchAt >= CONFIG.footballMatchIntervalMs) {
        const matches = Math.floor((now - state.football.lastMatchAt) / CONFIG.footballMatchIntervalMs);
        const perMatch = computeFootballMatchIncome();
        addMoney(perMatch * matches);
        state.football.lastMatchAt += matches * CONFIG.footballMatchIntervalMs;
      }
    }

    // Forex and stock updates
    if (now - (state.bank.forex.lastUpdate || 0) >= CONFIG.forexUpdateIntervalMs) {
      updateForexPrices(now - (state.bank.forex.lastUpdate || now));
      state.bank.forex.lastUpdate = now;
      if (state.ui.currentTab === 'invest') renderBank();
    }
    if (now - (state.bank.stock.lastUpdate || 0) >= CONFIG.stockUpdateIntervalMs) {
      updateStockPrice(now - (state.bank.stock.lastUpdate || now));
      state.bank.stock.lastUpdate = now;
      maybePayStockDividend();
      if (state.ui.currentTab === 'invest') renderBank();
    }

    // Daily interest accrual for vadesiz
    accrueVadesizInterestIfNeeded();
    // Also accrue loan interests to keep previews fresh
    for (const loan of state.bank.loans) {
      // passive preview only, do not mutate principal every second; accrue on repay or once per day
    }

    // Update UI timers
    renderHeader();
    renderLevel();
    renderGift();
    renderAd();
    if (state.ui.currentTab === 'companies') renderFootball();

  }, 1000);

  // Auto-save
  setInterval(() => saveState(), 30 * 1000);

  // Initial render and tab
  fullRender();
  switchTab(state.ui.currentTab || 'home');
})();