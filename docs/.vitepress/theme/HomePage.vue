<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref } from "vue";

const rootEl = ref<HTMLElement | null>(null);
const cleanupFns: Array<() => void> = [];

onMounted(() => {
  const root = rootEl.value;
  if (!root) return;

  const nav = root.querySelector<HTMLElement>("#main-nav");
  const menuBtn = root.querySelector<HTMLButtonElement>(".menu-toggle");

  if (menuBtn && nav) {
    const onToggle = () => {
      const isOpen = nav.classList.toggle("open");
      menuBtn.setAttribute("aria-expanded", String(isOpen));
    };
    menuBtn.addEventListener("click", onToggle);
    cleanupFns.push(() => menuBtn.removeEventListener("click", onToggle));

    nav.querySelectorAll("a").forEach((link) => {
      const onClose = () => {
        nav.classList.remove("open");
        menuBtn.setAttribute("aria-expanded", "false");
      };
      link.addEventListener("click", onClose);
      cleanupFns.push(() => link.removeEventListener("click", onClose));
    });
  }

  if (window.IntersectionObserver) {
    const revealEls = root.querySelectorAll<HTMLElement>(".reveal");
    const revealObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("in");
            revealObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.18 },
    );
    revealEls.forEach((el) => revealObserver.observe(el));
    cleanupFns.push(() => revealObserver.disconnect());

    const counters = root.querySelectorAll<HTMLElement>("[data-count]");
    const timers: number[] = [];
    const counterObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const el = entry.target as HTMLElement;
          const target = Number(el.getAttribute("data-count") || 0);
          let value = 0;
          const step = Math.max(1, Math.floor(target / 24));

          const timer = window.setInterval(() => {
            value += step;
            if (value >= target) {
              value = target;
              window.clearInterval(timer);
            }
            el.textContent = `${value}+`;
          }, 26);
          timers.push(timer);

          counterObserver.unobserve(el);
        });
      },
      { threshold: 0.42 },
    );
    counters.forEach((el) => counterObserver.observe(el));

    cleanupFns.push(() => {
      counterObserver.disconnect();
      timers.forEach((t) => window.clearInterval(t));
    });
  }
});

onBeforeUnmount(() => {
  cleanupFns.splice(0).forEach((fn) => fn());
});
</script>

<template>
  <div ref="rootEl" class="home-shell">
    <div class="bg-orb bg-orb-a"></div>
    <div class="bg-orb bg-orb-b"></div>

    <header class="header container">
      <a class="brand" href="#top">Axiom</a>
      <button class="menu-toggle" aria-label="切换菜单" aria-expanded="false">菜单</button>
      <nav class="nav" id="main-nav">
        <a href="#features">能力</a>
        <a href="#workflow">流程</a>
        <a href="#scenes">场景</a>
        <a href="#faq">FAQ</a>
        <a class="btn btn-sm" href="https://github.com/QingJ01/Axiom" target="_blank" rel="noreferrer">GitHub</a>
      </nav>
    </header>

    <main id="top">
      <section class="hero container reveal">
        <p class="chip">AI Native Development System</p>
        <h1>把 AI 从一次性问答，升级为长期可协作的工程伙伴</h1>
        <p class="lead">
          Axiom 通过 <strong>记忆层 + 流程层 + 协作层</strong>，让 Gemini / Claude / Codex / OpenCode / Copilot
          在真实项目中保持上下文、遵循门禁、持续交付。
        </p>
        <div class="hero-actions">
          <a class="btn" href="/guide/quickstart">立即开始</a>
          <a class="btn btn-ghost" href="#workflow">查看流程</a>
        </div>
        <div class="metrics">
          <article>
            <h3 data-count="5">0</h3>
            <p>主流 AI 工具适配</p>
          </article>
          <article>
            <h3 data-count="13">0</h3>
            <p>内置工作流</p>
          </article>
          <article>
            <h3 data-count="111">0</h3>
            <p>系统文件模块化沉淀</p>
          </article>
        </div>
      </section>

      <section class="section container reveal" id="features">
        <div class="section-head">
          <p class="chip">Core Capabilities</p>
          <h2>三层结构，保证 AI 行为可追踪、可复盘、可演进</h2>
        </div>
        <div class="cards">
          <article class="card">
            <h3>记忆层</h3>
            <p>保存项目决策、用户偏好与活动上下文，避免每轮对话从零开始。</p>
            <ul>
              <li>长期决策沉淀</li>
              <li>跨会话恢复任务</li>
              <li>知识与模式自动收割</li>
            </ul>
          </article>
          <article class="card">
            <h3>流程层</h3>
            <p>把需求评审、任务拆解、实现、验证串成闭环，门禁依赖可验证产物。</p>
            <ul>
              <li>Manifest-Driven</li>
              <li>Evidence-Based Gates</li>
              <li>增量交付可回滚</li>
            </ul>
          </article>
          <article class="card">
            <h3>协作层</h3>
            <p>统一适配不同 AI 工具，保持一致指令语义与团队协作节奏。</p>
            <ul>
              <li>多模型协同</li>
              <li>统一项目入口 `.agent/`</li>
              <li>低侵入接入业务代码</li>
            </ul>
          </article>
        </div>
      </section>

      <section class="section container reveal" id="workflow">
        <div class="section-head">
          <p class="chip">Workflow</p>
          <h2>从 `/start` 到交付，全流程自动接力</h2>
        </div>
        <ol class="timeline">
          <li><span>01</span>加载记忆与上下文：恢复任务状态与项目约束</li>
          <li><span>02</span>需求评审与 PRD：先定目标，再拆任务</li>
          <li><span>03</span>编码执行与自检：失败最多 3 次重试并熔断</li>
          <li><span>04</span>测试通过后交付：结果记录、知识收割、可持续进化</li>
        </ol>
      </section>

      <section class="section container reveal" id="scenes">
        <div class="section-head">
          <p class="chip">Use Cases</p>
          <h2>最适合这些团队与项目场景</h2>
        </div>
        <div class="scene-grid">
          <article>
            <h3>复杂需求项目</h3>
            <p>需求必须先评审、拆解、门禁验收，拒绝“直接写代码”的失控节奏。</p>
          </article>
          <article>
            <h3>多模型并行开发</h3>
            <p>不同 AI 工具各有优势，Axiom 提供统一工作系统做编排。</p>
          </article>
          <article>
            <h3>长期持续迭代</h3>
            <p>跨天开发保持上下文连续，经验自动沉淀为团队资产。</p>
          </article>
        </div>
      </section>

      <section class="section container reveal" id="faq">
        <div class="section-head">
          <p class="chip">FAQ</p>
          <h2>常见问题</h2>
        </div>
        <div class="faq-list">
          <details>
            <summary>会污染业务代码吗？</summary>
            <p>不会。Axiom 主要落在 `.agent/` 和文档目录，对业务代码侵入很低。</p>
          </details>
          <details>
            <summary>支持哪些技术栈？</summary>
            <p>内置 Flutter / React / Vue / Django / Express / Gin 模板，也支持自定义。</p>
          </details>
          <details>
            <summary>如何快速体验？</summary>
            <p>安装后在项目内输入 `/start`，再按 `/feature-flow` 走一遍完整交付链路即可。</p>
          </details>
        </div>
      </section>
    </main>

    <footer class="footer container reveal">
      <p>© 2026 Axiom. AI engineering runtime for real projects.</p>
      <a href="https://github.com/QingJ01/Axiom" target="_blank" rel="noreferrer">View on GitHub</a>
    </footer>
  </div>
</template>

<style scoped src="../../css/main.css"></style>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap");

.home-shell {
  --bg: #091222;
  --bg-soft: #0f1d34;
  --text: #f4f7fb;
  --muted: #b6c0d4;
  --primary: #44d4a2;
  --accent: #ffb454;
  --panel: rgba(255, 255, 255, 0.06);
  --border: rgba(255, 255, 255, 0.12);
  --shadow: 0 16px 60px rgba(0, 0, 0, 0.35);
  min-height: 100vh;
  color: #f4f7fb;
  font-family: "Noto Sans SC", sans-serif;
  background: radial-gradient(circle at 12% 10%, #18335f 0%, #091222 48%),
    linear-gradient(145deg, #081021, #0d1a30 60%, #112540);
  line-height: 1.6;
  overflow-x: hidden;
  padding-bottom: 1rem;
}
</style>
