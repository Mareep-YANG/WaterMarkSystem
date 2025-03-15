<template>
  <div class="login-container"><!-- 登录页面的容器 -->
    <el-card class="login-card"><!-- 登录卡片，使用Element UI的el-card组件 -->
      <template #header><!-- 头部模板区域，用于放置标题 -->
        <h2>登录</h2><!-- 登录页面的标题 -->
      </template>
      
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="80px"
        @submit.prevent="handleSubmit"
      ><!-- 表单区域，使用Element UI的el-form组件 -->
      
        <el-form-item label="用户名" prop="username"><!-- 用户名输入框 -->
          <el-input
            v-model="formData.username"
            placeholder="请输入用户名"
            :prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password"><!-- 密码输入框 -->
          <el-input
            v-model="formData.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item><!-- 提交按钮 -->
          <el-button
            type="primary"
            native-type="submit"
            :loading="loading"
            class="submit-btn"
          >
            登录
          </el-button>
        </el-form-item>
        
        <div class="form-footer"><!-- 注册链接 -->
          <router-link to="/register">
            还没有账号？立即注册
          </router-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'; // 引入Vue的ref和reactive函数
import { useRouter, useRoute } from 'vue-router'; // 引入Vue Router的useRouter和useRoute函数
import { ElMessage } from 'element-plus'; // 引入Element Plus的消息组件
import { User, Lock } from '@element-plus/icons-vue'; // 引入Element Plus的图标
import type { FormInstance } from 'element-plus'; // 引入Element Plus的FormInstance类型
import { useUserStore } from '@/stores'; // 引入用户存储

const router = useRouter(); // 获取路由实例
const route = useRoute(); // 获取当前路由
const userStore = useUserStore(); // 获取用户存储实例

const formRef = ref<FormInstance>(); // 表单引用
const loading = ref(false); // 加载状态

const formData = reactive({
  username: '', // 用户名
  password: '', // 密码
});

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }, // 用户名必填规则
    { min: 3, message: '用户名至少3个字符', trigger: 'blur' }, // 用户名长度规则
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }, // 密码必填规则
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }, // 密码长度规则
  ],
};

const handleSubmit = async () => {
  if (!formRef.value) return; // 如果表单引用不存在，直接返回
  
  try {
    await formRef.value.validate(); // 使用 formRef.value.validate() 验证表单数据是否满足预设的验证规则
    loading.value = true; // 设置 loading 状态为 true，可用于显示加载中的动画和禁用提交按钮
    
    await userStore.login(formData.username, formData.password); // 调用登录方法
    ElMessage.success('登录成功'); // 显示成功消息
    
    // 如果有重定向地址，则跳转到重定向地址
    const redirect = route.query.redirect as string;
    router.push(redirect || '/'); // 跳转到重定向地址或首页
  } catch (error: any) {
    ElMessage.error(error.message || '登录失败'); // 显示错误消息
  } finally {
    loading.value = false; // 设置加载状态为false
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.login-card {
  width: 400px;
}

.submit-btn {
  width: 100%;
}

.form-footer {
  margin-top: 20px;
  text-align: center;
}

.form-footer a {
  color: #409EFF;
  text-decoration: none;
}

.form-footer a:hover {
  color: #66b1ff;
}
</style>