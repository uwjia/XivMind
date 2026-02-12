import type { Preview } from '@storybook/vue3-vite';
import { setup } from '@storybook/vue3-vite';
import { createPinia } from 'pinia';
import { createRouter, createWebHistory } from 'vue-router';
import '../src/style.css';

// Create a simple router for Storybook
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: {} },
    { path: '/search', component: {} }
  ]
});

const pinia = createPinia();

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    backgrounds: {
      default: '#ffffff',
      values: [
        { name: 'Light', value: '#ffffff' },
        { name: 'Dark', value: '#1a1a1a' },
      ],
    },
  },
};

setup((app) => {
  app.use(router);
  app.use(pinia);
});

export default preview;