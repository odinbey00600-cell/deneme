const botData = [
  {
    id: "Bot-1",
    color: "#ff4976",
    balance: 0,
    leverage: "125x",
    pnl: "-$100.00 (-100%)",
    side: "LONG 0.025 BTC @ $43,250",
    liq: "Likidasyon: $42,890 | Marjin: $0.80",
    tpSl: "TP: $44,500 | SL: --",
    strategy: "Aşırı kaldıraç, stop-loss yok",
    confidence: 15,
  },
  {
    id: "Bot-2",
    color: "#15f5a2",
    balance: 145,
    leverage: "80x",
    pnl: "+$45.00 (+45%)",
    side: "SHORT 0.031 BTC @ $44,010",
    liq: "Likidasyon: $44,980 | Marjin: $1.21",
    tpSl: "TP: $43,520 | SL: $44,240",
    strategy: "Funding aşırı + momentum kırılımı",
    confidence: 84,
  },
  {
    id: "Bot-3",
    color: "#3da5ff",
    balance: 112.45,
    leverage: "125x",
    pnl: "+$12.45 (+12.45%)",
    side: "LONG 0.025 BTC @ $43,250",
    liq: "Likidasyon: $42,890 | Marjin: $0.80",
    tpSl: "TP: $44,500 | SL: $42,900",
    strategy: "Trend takibi + RSI aşırı satım",
    confidence: 78,
  },
];

const symbolCards = document.querySelector("#symbolCards");
const tabsEl = document.querySelector("#botTabs");
const summaryEl = document.querySelector("#botSummary");
const decisionEl = document.querySelector("#decisionExplain");
const countdownEl = document.querySelector("#fundingCountdown");
const ratioEl = document.querySelector("#longShortRatio");
const edgeGlow = document.querySelector("#edgeGlow");

let selected = Number(localStorage.getItem("selectedBot") || 2);

function renderSymbols() {
  const rows = [
    { pair: "BTC/USDT", price: 43250, change: 1.12 },
    { pair: "ETH/USDT", price: 2310, change: -0.44 },
    { pair: "SOL/USDT", price: 101.3, change: 3.01 },
    { pair: "BNB/USDT", price: 587.2, change: -1.78 },
  ];

  symbolCards.innerHTML = rows
    .map(
      (x) => `<div class="symbol-card">
      <small>${x.pair}</small>
      <strong>$${x.price.toLocaleString()}</strong>
      <small class="${x.change >= 0 ? "positive" : "negative"}">${x.change >= 0 ? "+" : ""}${x.change}%</small>
    </div>`
    )
    .join("");
}

function renderTabs() {
  tabsEl.innerHTML = "";
  botData.forEach((bot, i) => {
    const button = document.createElement("button");
    button.className = `btn bot-tab ${i === selected ? "active" : ""}`;
    button.style.borderColor = i === selected ? bot.color : "";
    button.textContent = bot.id;
    button.onclick = () => {
      selected = i;
      localStorage.setItem("selectedBot", String(i));
      renderTabs();
      renderSummary();
    };
    tabsEl.appendChild(button);
  });
}

function renderSummary() {
  const bot = botData[selected];
  const pnlClass = bot.pnl.includes("+") ? "positive" : "negative";
  summaryEl.innerHTML = `<pre>Bakiye: $${bot.balance.toFixed(2)} USDT
Kaldıraç: ${bot.leverage}
PnL: <span class="${pnlClass}">${bot.pnl}</span>

Aktif Pozisyon:
${bot.side}
${bot.liq}
${bot.tpSl}

AI Strateji Durumu:
"${bot.strategy}"
Güven skoru: ${bot.confidence}%</pre>`;

  decisionEl.textContent = `${bot.id}, son işlemde 15m trend + 1m giriş filtresi kullandı. Volatilite yükseldiğinde Sakin Mod ile pozisyon boyutunu azaltmayı öneriyor.`;
}

function renderDepth() {
  const asks = document.querySelector("#asksBars");
  const bids = document.querySelector("#bidsBars");

  const draw = (node, reverse = false) => {
    node.innerHTML = "";
    Array.from({ length: 14 }, (_, i) => (reverse ? 90 - i * 6 : 10 + i * 6)).forEach((width) => {
      const bar = document.createElement("div");
      bar.className = "bar";
      bar.style.width = `${width}%`;
      node.appendChild(bar);
    });
  };

  draw(asks, true);
  draw(bids, false);
}

function renderHeatmap() {
  const heatmap = document.querySelector("#heatmap");
  heatmap.innerHTML = "";
  for (let i = 0; i < 60; i++) {
    const cell = document.createElement("div");
    cell.className = "heat";
    cell.style.setProperty("--a", (Math.random() * 0.7 + 0.1).toFixed(2));
    heatmap.appendChild(cell);
  }
}

function startFundingCountdown() {
  let remaining = 2 * 60 * 60 + 17 * 60 + 35;
  setInterval(() => {
    remaining = remaining > 0 ? remaining - 1 : 8 * 60 * 60;
    const h = String(Math.floor(remaining / 3600)).padStart(2, "0");
    const m = String(Math.floor((remaining % 3600) / 60)).padStart(2, "0");
    const s = String(remaining % 60).padStart(2, "0");
    countdownEl.textContent = `${h}:${m}:${s}`;
    ratioEl.textContent = (1 + Math.sin(Date.now() / 5000) * 0.1 + 0.04).toFixed(2);
  }, 1000);
}

function registerPanicButton() {
  document.querySelector("#panicBtn").addEventListener("click", () => {
    edgeGlow.style.borderColor = "rgba(255,73,118,0.75)";
    edgeGlow.style.boxShadow = "inset 0 0 40px rgba(255,73,118,0.5)";
    setTimeout(() => {
      edgeGlow.style.borderColor = "transparent";
      edgeGlow.style.boxShadow = "none";
    }, 1200);
  });
}

function renderDNA() {
  document.querySelector("#dnaPreview").textContent = JSON.stringify(
    {
      botId: "bot_3",
      generation: 3,
      inheritance: ["bot_1", "bot_2"],
      learnedRules: [
        "Never 125x without SL",
        "Avoid trading 30min before FOMC",
        "If funding > 0.1%, prefer short",
      ],
      dna: {
        riskAppetite: 0.7,
        indicatorWeights: { rsi: 0.3, macd: 0.5, volume: 0.2 },
      },
    },
    null,
    2
  );
}

renderSymbols();
renderTabs();
renderSummary();
renderDepth();
renderHeatmap();
renderDNA();
registerPanicButton();
startFundingCountdown();
