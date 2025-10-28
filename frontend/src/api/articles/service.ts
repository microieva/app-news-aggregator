import { apiClient } from '@/api/client';
import { ArticlesData } from '@/types/api';

export const articlesService = {
  async getArticles(): Promise<ArticlesData> {
    return await apiClient.get<ArticlesData>('/articles/with-summaries');
  },

};