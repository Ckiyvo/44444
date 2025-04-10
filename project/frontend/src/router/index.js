import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '../components/HomePage.vue';
import ProjectManagement from '../components/ProjectManagement.vue';

import UserManagement from '../components/UserManagement.vue';
import ProjectDetail from '../components/ProjectDetail.vue'; 
import FileDetail from '../components/FileDetail.vue';


const routes = [
  {
    path: '/',
    name: 'HomePage',
    component: HomePage
  },
  {
    path: '/project',
    name: 'ProjectManagement',
    component: ProjectManagement
  },
  {
    path: '/project/:projectName',
    name: 'ProjectDetail',
    component: ProjectDetail,
    props: true
  },
  {
    path: '/project/:projectname/:filename',
    name: 'FileDetail',
    component: FileDetail
  },
  {
    path: '/user-management',
    name: 'UserManagement',
    component: UserManagement
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;