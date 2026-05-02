const timeline = [
  {
    title: "DocumentParserAgent",
    text: "读取合同文本并抽取付款、验收、责任、续约、IP 与数据条款。",
  },
  {
    title: "ClauseComparisonAgent",
    text: "将结构化字段与规则库比对，识别超过阈值的单点风险。",
  },
  {
    title: "RiskReasoningAgent",
    text: "组合多个风险信号，生成现金流、合规、责任失衡等复合风险。",
  },
  {
    title: "ReportAgent",
    text: "输出审查结论、处理建议、人工复核标记和可交付报告。",
  },
];

const contractSummary = {
  high_risk_saas_contract:
    "该合同包含长账期、长验收、自动续约、无限责任、知识产权让渡和数据跨境等多个风险信号，适合作为高风险合同初审样例。",
  low_risk_saas_contract:
    "该合同采用较短账期、默认验收、责任封顶和境内数据处理要求，整体更接近标准 SaaS 服务合同控制线。",
};

const uiMap = {
  high_risk_saas_contract: { badge: "高优先级处理", review: "Required" },
  low_risk_saas_contract: { badge: "可快速放行", review: "Optional" },
};

async function loadData() {
  const response = await fetch("./data/reviews.json");
  return response.json();
}

function formatMetric(label, value) {
  return `
    <div class="metric">
      <span class="metric-label">${label}</span>
      <span class="metric-value">${value}</span>
    </div>
  `;
}

function renderTimeline(container) {
  container.innerHTML = timeline
    .map(
      (item, index) => `
        <article class="timeline-step">
          <span>${index + 1}</span>
          <h3>${item.title}</h3>
          <p>${item.text}</p>
        </article>
      `
    )
    .join("");
}

function renderFindings(container, findings) {
  if (!findings.length) {
    container.innerHTML = `
      <article class="finding">
        <div class="finding-head">
          <h3>未发现明显超阈值风险</h3>
          <span class="severity low">low</span>
        </div>
        <p>该样例合同在付款周期、责任边界、数据处理和知识产权上都较为稳妥。</p>
      </article>
    `;
    return;
  }

  container.innerHTML = findings
    .map(
      (finding) => `
        <article class="finding">
          <div class="finding-head">
            <h3>${finding.title}</h3>
            <span class="severity ${finding.severity}">${finding.severity}</span>
          </div>
          <p>${finding.reason}</p>
          <p class="finding-reco">${finding.recommendation}</p>
        </article>
      `
    )
    .join("");
}

function renderChainRisks(container, chainRisks) {
  if (!chainRisks.length) {
    container.innerHTML = `
      <article class="chain-item">
        <h3>未触发复合风险链</h3>
        <p>当前样例没有出现需要升级处理的组合型风险。</p>
      </article>
    `;
    return;
  }

  container.innerHTML = chainRisks
    .map(
      (item) => `
        <article class="chain-item">
          <h3>Chain Risk</h3>
          <p>${item}</p>
        </article>
      `
    )
    .join("");
}

function updateDashboard(data, contractId) {
  const review = data[contractId];
  const { features, findings, assessment } = review;
  const meta = uiMap[contractId];
  const riskScore = assessment.risk_score;

  document.getElementById("contract-title").textContent = features.contract_title;
  document.getElementById("contract-summary").textContent = contractSummary[contractId];
  document.getElementById("risk-score").textContent = riskScore;
  document.getElementById("risk-level").textContent = assessment.risk_level;
  document.getElementById("risk-review").textContent = meta.review;
  document.getElementById("status-badge").textContent = meta.badge;
  document.getElementById("findings-count").textContent = `${findings.length} findings`;

  const ring = document.getElementById("risk-ring");
  ring.style.setProperty("--risk-fill", `${Math.max(riskScore * 3.6, 3.6)}deg`);

  document.getElementById("metrics-grid").innerHTML = [
    formatMetric("付款周期", features.payment_days == null ? "未识别" : `${features.payment_days} 天`),
    formatMetric("验收周期", features.acceptance_days == null ? "未识别" : `${features.acceptance_days} 天`),
    formatMetric("自动续约", features.auto_renewal ? "是" : "否"),
    formatMetric("人工复核", assessment.requires_human_review ? "建议" : "可选"),
  ].join("");

  renderFindings(document.getElementById("findings-list"), findings);
  renderChainRisks(document.getElementById("chain-list"), assessment.chain_risks);

  document.querySelectorAll("[data-contract]").forEach((button) => {
    button.classList.toggle("active", button.dataset.contract === contractId);
  });
}

async function bootstrap() {
  const data = await loadData();
  renderTimeline(document.getElementById("timeline"));
  updateDashboard(data, "high_risk_saas_contract");

  document.querySelectorAll("[data-contract]").forEach((button) => {
    button.addEventListener("click", () => updateDashboard(data, button.dataset.contract));
  });
}

bootstrap();
