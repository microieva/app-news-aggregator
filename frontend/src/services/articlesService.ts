import { ApiResponse, ArticlesData, SourcesData } from '@/types/api';
import { Article } from '@/types/article';
import { apiClient } from '@/utils/client';

export const articlesService = {

  async getArticles(source?: string, skip: number = 0, limit: number = 100): Promise<ArticlesData> {
    const config = source ? { params: { source } } : undefined;
    try {
      const response =  await apiClient.get<ApiResponse<ArticlesData>>('/articles/with-summaries', config);
      return response.data;
    } catch (error) {
      console.error('Error fetching topics:', error);
      throw error;
    }
  },

  async getArticlesByTopicName(topic:string, source?:string): Promise<ArticlesData> {
    try {
      const config = source ? { params: { source } } : undefined;
      const response =  await apiClient.get<ApiResponse<ArticlesData>>(`/articles/topic-name/${encodeURIComponent(topic)}`, config);
      return response.data;
    } catch (error) {
      console.error('Error fetching articles:', error);
      throw error;
    }
  },

  async getFrontPageArticles(source?: string): Promise<ArticlesData> {
    try {
      const config = source ? { params: { source } } : undefined;
      const response =  await apiClient.get<ApiResponse<ArticlesData>>('/articles/with-summaries', config);
      return response.data;
    } catch (error) {
      console.error('Error fetching articles:', error);
      throw error;
    }
  },

  async getArticleById(id: string): Promise<Article> {
    try {
      const response = await apiClient.get<ApiResponse<Article>>(`/articles/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching article ${id}:`, error);
      throw error;
    }
  },

  async getUsedSources(): Promise<SourcesData> {
    try {
      const repsonse =  await apiClient.get<ApiResponse<SourcesData>>(`/articles/sources`);
      return repsonse.data;
    } catch (error) {
      console.error('Error fetching used sources:', error);
      throw error;
    }
  },

  async searchArticles(query:string): Promise<any>{
    try {

    } catch (error) {
      console.error('Error fetching used sources:', error);
      throw error;
    }
  }
}

