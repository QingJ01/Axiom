import { defineConfig } from "vitepress";

export default defineConfig({
  lang: "zh-CN",
  title: "Axiom",
  description: "Axiom 项目介绍与使用教程",
  cleanUrls: true,
  lastUpdated: true,
  themeConfig: {
    siteTitle: "Axiom",
    logo: '/logo.svg',
    nav: [
      { text: "首页", link: "/" },
      { text: "安装", link: "/guide/install-and-upgrade" },
      { text: "系统原理", link: "/concepts/how-it-works" },
      { text: "命令参考", link: "/guide/commands" }
    ],
    sidebar: [
      {
        text: "使用指南",
        items: [
          { text: "快速开始", link: "/guide/quickstart" },
          { text: "安装、升级与卸载", link: "/guide/install-and-upgrade" },
          { text: "实战教程", link: "/guide/tutorial" },
          { text: "工作流说明", link: "/guide/workflows" },
          { text: "命令参考", link: "/guide/commands" },
          { text: "故障排查", link: "/guide/troubleshooting" }
        ]
      },
      {
        text: "系统参考",
        items: [
          { text: "目录结构", link: "/reference/structure" },
          { text: "配置说明", link: "/reference/configuration" },
          { text: "版本发布", link: "/reference/release" },
          { text: "更新日志", link: "/reference/changelog" }
        ]
      },
      {
        text: "概念与原理",
        items: [
          { text: "项目用途与边界", link: "/concepts/purpose-and-scope" },
          { text: "功能地图", link: "/concepts/feature-map" },
          { text: "系统工作原理", link: "/concepts/how-it-works" },
          { text: "原理 Q&A", link: "/concepts/principle-qa" }
        ]
      },
      {
        text: "关于项目",
        items: [
          { text: "关于项目", link: "/concepts/about-project" }
        ]
      }
    ],
    search: {
      provider: "local"
    },
    outline: {
      level: [2, 3],
      label: "目录"
    },
    docFooter: {
      prev: "上一页",
      next: "下一页"
    },
    lastUpdated: {
      text: "最后更新"
    }
  }
});
