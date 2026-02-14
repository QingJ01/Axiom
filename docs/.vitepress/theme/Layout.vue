<script setup lang="ts">
import DefaultTheme from "vitepress/theme";
import { useData } from "vitepress";
import HomePage from "./HomePage.vue";

const { page } = useData();
</script>

<template>
  <HomePage v-if="page.relativePath === 'index.md'" />
  <DefaultTheme.Layout v-else />
</template>
