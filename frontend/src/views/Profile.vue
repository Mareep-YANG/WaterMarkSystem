<template>
  <div class="profile-container"><!-- 个人信息页面的容器 -->
    <el-row :gutter="20"><!-- 使用Element UI的el-row组件，设置列间距为20 -->
      <el-col :span="8"><!-- 使用Element UI的el-col组件，设置列宽度为8 -->
        <el-card><!-- 个人信息卡片 -->
          <template #header><!-- 头部模板区域 -->
            <div class="card-header">
              <h3>个人信息</h3><!-- 个人信息标题 -->
            </div>
          </template>

          <el-descriptions border><!-- 个人信息描述 -->
            <el-descriptions-item label="用户名">
              {{ user?.username }}
            </el-descriptions-item>
            <el-descriptions-item label="邮箱">
              {{ user?.email }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="user?.is_active ? 'success' : 'danger'">
                {{ user?.is_active ? '正常' : '禁用' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <el-col :span="16"><!-- 使用Element UI的el-col组件，设置列宽度为16 -->
        <el-card><!-- API密钥管理卡片 -->
          <template #header><!-- 头部模板区域 -->
            <div class="card-header">
              <h3>API密钥管理</h3><!-- API密钥管理标题 -->
              <el-button
                type="primary"
                size="small"
                @click="handleCreateApiKey"
              >
                创建密钥
              </el-button>
            </div>
          </template>

          <el-alert
            v-if="newApiKey"
            type="success"
            :closable="false"
            class="mb-20"
          >
            <template #default>
              <p>请保存您的新API密钥，此密钥仅显示一次：</p>
              <el-input v-model="newApiKey" readonly>
                <template #append>
                  <el-button @click="copyApiKey">复制</el-button>
                </template>
              </el-input>
            </template>
          </el-alert>

          <el-table :data="apiKeys" stripe style="width: 100%"><!-- API密钥列表 -->
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="created_at" label="创建时间">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button
                  type="danger"
                  size="small"
                  @click="handleRevokeApiKey(row.id)"
                >
                  撤销
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog
      v-model="dialogVisible"
      title="创建API密钥"
      width="400px"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-position="top"
      >
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            placeholder="请输入密钥描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitApiKey">
            确认
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'; // 引入Vue的相关函数
import { ElMessage, ElMessageBox } from 'element-plus'; // 引入Element Plus的消息组件
import type { FormInstance } from 'element-plus'; // 引入Element Plus的FormInstance类型
import { useUserStore } from '@/stores'; // 引入用户存储
import api from '@/api'; // 引入API模块

interface ApiKey {
  id: string;
  description: string;
  created_at: string;
}

const userStore = useUserStore(); // 获取用户存储实例
const user = computed(() => userStore.currentUser); // 计算属性，获取当前用户信息

const apiKeys = ref<ApiKey[]>([]); // API密钥列表
const newApiKey = ref(''); // 新创建的API密钥
const dialogVisible = ref(false); // 创建API密钥对话框的可见性
const formRef = ref<FormInstance>(); // 表单引用

const formData = reactive({
  description: '', // 表单数据，密钥描述
});

const rules = {
  description: [
    { required: true, message: '请输入密钥描述', trigger: 'blur' }, // 密钥描述必填规则
    { min: 3, message: '描述至少3个字符', trigger: 'blur' }, // 密钥描述长度规则
  ],
};

const formatDate = (date: string) => {
  return new Date(date).toLocaleString(); // 格式化日期
};

const fetchApiKeys = async () => {
  try {
    const response = await api.auth.getApiKeys(); // 获取API密钥列表
    apiKeys.value = response;
  } catch (error) {
    ElMessage.error('获取API密钥列表失败'); // 显示错误消息
  }
};

const handleCreateApiKey = () => {
  formData.description = ''; // 清空表单数据
  dialogVisible.value = true; // 显示创建API密钥对话框
};

const submitApiKey = async () => {
  if (!formRef.value) return;
  
  try {
    await formRef.value.validate(); // 验证表单数据
    const response = await api.auth.createApiKey(formData.description); // 创建API密钥
    newApiKey.value = response.key; // 保存新创建的API密钥
    dialogVisible.value = false; // 关闭对话框
    await fetchApiKeys(); // 重新获取API密钥列表
    ElMessage.success('API密钥创建成功'); // 显示成功消息
  } catch (error: any) {
    ElMessage.error(error.message || 'API密钥创建失败'); // 显示错误消息
  }
};

const handleRevokeApiKey = async (id: string) => {
  try {
    await ElMessageBox.confirm(
      '确定要撤销此API密钥吗？此操作不可恢复',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );
    
    await api.auth.revokeApiKey(id); // 撤销API密钥
    await fetchApiKeys(); // 重新获取API密钥列表
    ElMessage.success('API密钥已撤销'); // 显示成功消息
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('API密钥撤销失败'); // 显示错误消息
    }
  }
};

const copyApiKey = () => {
  navigator.clipboard.writeText(newApiKey.value) // 复制API密钥到剪贴板
    .then(() => {
      ElMessage.success('API密钥已复制到剪贴板'); // 显示成功消息
    })
    .catch(() => {
      ElMessage.error('复制失败，请手动复制'); // 显示错误消息
    });
};

onMounted(async () => {
  await fetchApiKeys(); // 组件挂载时获取API密钥列表
});
</script>

<style scoped>
.profile-container {
  padding: 20px; /* 设置容器内边距 */
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center; /* 设置头部内容的对齐方式 */
}

.mb-20 {
  margin-bottom: 20px; /* 设置下边距 */
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px; /* 设置按钮间距 */
}
</style>