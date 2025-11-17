import { apiClient } from '@/utils/client';
import { ApiResponse, ArticlesData, SearchData, SourcesData } from '@/types/api';
import { Article, SearchParams } from '@/types/article';

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

  async searchArticles(searchParams:SearchParams): Promise<any>{
    const params = {
      ...searchParams,
      topic_id: searchParams.topic?.id || null,
      published_after: searchParams.publishedAfter || null,
      published_before: searchParams.publishedBefore || null,
      sort_by: searchParams.sortBy 
    }
    const config = {params}
    try {
      const repsonse =  await apiClient.get<ApiResponse<SearchData>>(`/articles/search`, config);
      return repsonse.data;
    } catch (error) {
      console.error('Error fetching used sources:', error);
      throw error;
    }
  }
}

