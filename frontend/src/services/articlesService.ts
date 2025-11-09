import { ArticlesData, SourcesData } from '@/types/api';
import { Article } from '@/types/article';
import { ApiClient } from '@/utils/client';


class ArticlesService {
  private apiClient: ApiClient;

  constructor() {
    this.apiClient = new ApiClient(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api');
  }

  async getArticles(source?: string, skip: number = 0, limit: number = 100): Promise<ArticlesData> {
    const config = source ? { params: { source } } : undefined;
    try {
      return await this.apiClient.get<ArticlesData>('/articles/with-summaries', config);
    } catch (error) {
      console.error('Error fetching topics:', error);
      throw error;
    }
  }

  async getArticlesByTopicName(topic:string, source?:string): Promise<ArticlesData> {
    try {
      const config = source ? { params: { source } } : undefined;
      return await this.apiClient.get<ArticlesData>(`/articles/topic-name/${encodeURIComponent(topic)}`, config);
    } catch (error) {
      console.error('Error fetching articles:', error);
      throw error;
    }
  }

  async getFrontPageArticles(source?: string): Promise<ArticlesData> {
    try {
      const config = source ? { params: { source } } : undefined;
      return await this.apiClient.get<ArticlesData>('/articles/with-summaries', config);
    } catch (error) {
      console.error('Error fetching articles:', error);
      throw error;
    }
  }

  async getArticleById(id: string): Promise<Article> {
    try {
      const data = await this.apiClient.get<Article>(`/articles/${id}`);
      return data;
    } catch (error) {
      console.error(`Error fetching article ${id}:`, error);
      throw error;
    }
  }

  async getUsedSources(): Promise<SourcesData> {
    try {
      return await this.apiClient.get<SourcesData>(`/articles/sources`);
    } catch (error) {
      console.error('Error fetching used sources:', error);
      throw error;
    }
  }
}

export const articlesService = new ArticlesService();

export default articlesService;