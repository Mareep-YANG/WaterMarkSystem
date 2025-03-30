<template>
  <el-config-provider :locale="zhCn">
    <div class="app-wrapper">
      <router-view v-slot="{ Component }">
        <transition name="fade">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import './assets/styles/index.css'
</script>

<style scoped>
.app-wrapper {
  height: 100%;
  width: 100%;
}

</style>