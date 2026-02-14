import { defineConfig } from "vitepress";

export default defineConfig({
  lang: "zh-CN",
  title: "Axiom",
  description: "Axiom 项目介绍与使用教程",
  cleanUrls: true,
  lastUpdated: true,
  themeConfig: {
    siteTitle: "Axiom",
    nav: [
      { text: "首页", link: "/" },
      { text: "快速开始", link: "/guide/quickstart" },
      { text: "实战教程", link: "/guide/tutorial" },
      { text: "命令参考", link: "/guide/commands" }
    ],
    sidebar: [
      {
        text: "使用指南",
        items: [
          { text: "快速开始", link: "/guide/quickstart" },
          { text: "安装与运行", link: "/guide/installation" },
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
          { text: "版本发布", link: "/reference/release" }
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
