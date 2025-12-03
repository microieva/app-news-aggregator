import { apiClient } from '@/utils/client';
import { ApiResponse, ArticlesData, HeadlinesData, SearchData, SourcesData } from '@/types/api';
import { Article, SearchParams } from '@/types/article';

export const articlesService = {

  async getArticles(source:string | null, page: number = 1, pageSize: number = 50 ): Promise<ArticlesData> {
    try {
      const skip = (page - 1) * pageSize;
      const config = source ? { params: { source, skip, limit:pageSize } } : undefined;
      const response =  await apiClient.get<ApiResponse<ArticlesData>>('/articles/', config);
      return response.data;
    } catch (error) {
      console.error('Error fetching articles:', error);
      throw error;
    }
  },

  async getArticlesByTopicId(topicId:string, source?:string, page: number = 1, pageSize: number = 4): Promise<ArticlesData> {
    try {
      const skip = (page - 1) * pageSize;
      const config = source ? { params: { source, skip, limit:pageSize } } : undefined;
      const response =  await apiClient.get<ApiResponse<ArticlesData>>(`/articles/topic/${encodeURIComponent(topicId)}`, config);
      return response.data;
    } catch (error) {
      console.error('Error fetching articles:', error);
      throw error;
    }
  },

  async getFrontPageArticles(source?: string): Promise<ArticlesData> {
    try {
      const config = source ? { params: { source } } : undefined;
      const response =  await apiClient.get<ApiResponse<ArticlesData>>('/articles/frontpage', config);
      return response.data;
    } catch (error) {
      console.error('Error fetching articles:', error);
      throw error;
    }
  },

  async getArticleById(article_id: string): Promise<Article> {
    try {
      const response = await apiClient.get<ApiResponse<Article>>(`/articles/article/${article_id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching article ${article_id}:`, error);
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
      console.error('Error searching articles:', error);
      throw error;
    }
  },

    async getHeadlines(page: number = 1, pageSize: number = 50 ): Promise<HeadlinesData> {
    try {
      const skip = (page - 1) * pageSize;
      const config = { params: { skip, limit:pageSize } };
      const response =  await apiClient.get<ApiResponse<HeadlinesData>>('/articles/headlines', config);
      return response.data;
    } catch (error) {
      console.error('Error fetching headlines:', error);
      throw error;
    }
  }
}

