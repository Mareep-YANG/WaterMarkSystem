import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'; // 引入Vue Router的相关函数和类型
import { useUserStore } from '@/stores'; // 引入 Pinia 的用户状态
import { ElMessage } from 'element-plus'; // 引入 Element Plus 的消息组件

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'), // 懒加载Home组件
    meta: { 
      requiresAuth: true,
      showNav: true
    } // 需要认证的页面
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'), // 懒加载Register组件
    meta: { 
      guest: true,
      showNav: false
    } // 游客页面
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'), // 懒加载Login组件
    meta: { 
      guest: true,
      showNav: false
    } // 游客页面
  },
  {
    path: '/watermark',
    name: 'Watermark',
    component: () => import('@/views/Watermark.vue'), // 懒加载Watermark组件
    meta: { 
      requiresAuth: true,
      showNav: true
    } // 需要认证的页面
  },
  {
    path: '/evaluate',
    name: 'Evaluate',
    component: () => import('@/views/Evaluate.vue'), // 懒加载Evaluate组件
    meta: { 
      requiresAuth: true,
      showNav: true
    } // 需要认证的页面
  },
  {
    path: '/models',
    name: 'ModelManagement',
    component: () => import('@/views/ModelManagement.vue'), // 懒加载model组件
    meta: {
      title: 'Model Management',
      requiresAuth: true,
      showNav: true
    } // 需要认证的页面
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'), // 懒加载Profile组件
    meta: { 
      requiresAuth: true,
      showNav: true
    } // 需要认证的页面
  },
  {
    path: '/dataset',
    name: 'Dataset',
    component: () => import('@/views/Dataset.vue'), // 懒加载model组件
    meta: {
      title: 'Dataset',
      requiresAuth: true,
      showNav: true
    } // 需要认证的页面
  }
];

const router = createRouter({
  history: createWebHistory(), // 使用HTML5历史模式
  routes // 路由配置
});

// 路由守卫
router.beforeEach((to, _from, next) => {
  const userStore = useUserStore();

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!userStore.token) {
      ElMessage.warning('请先登录以访问该页面');
      next({
        path: '/login',
        query: { redirect: to.fullPath },
      });
    } else {
      next();
    }
  } else if (to.matched.some(record => record.meta.guest)) {
    if (userStore.token) {
      ElMessage.info('您已登录，正在跳转到首页');
      next('/');
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router; // 导出路由实例