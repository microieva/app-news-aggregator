import { ArticlesData } from '@/types/api';
import { Article } from '@/types/article';
import { ApiClient } from '@/utils/client';


class ArticlesService {
  private apiClient: ApiClient;

  constructor() {
    this.apiClient = new ApiClient(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api');
  }

  async getArticles(skip: number = 0, limit: number = 100): Promise<ArticlesData> {
    try {
      return await this.apiClient.get<ArticlesData>('/articles/with-summaries');
    } catch (error) {
      console.error('Error fetching topics:', error);
      throw error;
    }
  }

  async getArticlesByTopicName(topic_name: string): Promise<ArticlesData> {
    const articles = localStorage.getItem(`articles_${topic_name}`) || undefined;
    if (articles) {
      return { articles: JSON.parse(articles) , total: JSON.parse(articles).length };
    } else {
      try {
        const data =  await this.apiClient.get<ArticlesData>(`/articles/topic-name/${encodeURIComponent(topic_name)}`, );
        localStorage.setItem(`articles_${topic_name}`, JSON.stringify(data.articles));
        return data;
      } catch (error) {
        console.error(`Error fetching topic ${name}:`, error);
        throw error;
      }
    }
  }

  async getFrontPageArticles(): Promise<ArticlesData> {
    const articles = localStorage.getItem('frontPageArticles') || undefined;
    if (articles) {
      return { articles: JSON.parse(articles) , total: JSON.parse(articles).length };
    } else {
      try {
        const data = await this.apiClient.get<ArticlesData>('/articles/front-page');
        localStorage.setItem('frontPageArticles', JSON.stringify(data.articles)); 
        return data;
      } catch (error) {
        console.error('Error fetching front page articles:', error);
        throw error;
      }
    }
  }

  async getArticleById(id: string): Promise<Article> {
    const article = localStorage.getItem(`article_${id}`) || undefined;
    if (article) {
      return JSON.parse(article);
    } else {
      try {
        const data = await this.apiClient.get<Article>(`/articles/${id}`);
        localStorage.setItem(`article_${id}`, JSON.stringify(data));
        return data;
      } catch (error) {
        console.error(`Error fetching article ${id}:`, error);
        throw error;
      }
    }
  }

  // async getUsedArticles(skip: number = 0, limit: number = 100): Promise<ArticlesData> {
  //   try {
  //     return await this.apiClient.get<ArticlesData>(`/topics/used`);
  //   } catch (error) {
  //     console.error('Error fetching used topics:', error);
  //     throw error;
  //   }
  // }

 

  // async getArticleByName(name: string): Promise<{ data: Article }> {
  //   try {
  //     return await this.apiClient.get<{ data: Article }>(`/topics/name/${encodeURIComponent(name)}`);
  //   } catch (error) {
  //     console.error(`Error fetching topic by name ${name}:`, error);
  //     throw error;
  //   }
  // }

  /**
   * Create a new topic
   */
  // async createArticle(topicData: Omit<Article, 'id' | 'created_at' | 'updated_at'>): Promise<{ data: Article }> {
  //   try {
  //     return await this.apiClient.post<{ data: Article }>('/topics', topicData);
  //   } catch (error) {
  //     console.error('Error creating topic:', error);
  //     throw error;
  //   }
  // }

  /**
   * Update an existing topic
   */
  // async updateArticle(id: string, topicData: Partial<Article>): Promise<{ data: Article }> {
  //   try {
  //     return await this.apiClient.put<{ data: Article }>(`/topics/${id}`, topicData);
  //   } catch (error) {
  //     console.error(`Error updating topic ${id}:`, error);
  //     throw error;
  //   }
  // }

  /**
   * Delete a topic
   */
  // async deleteArticle(id: string): Promise<{ success: boolean; message: string }> {
  //   try {
  //     return await this.apiClient.delete<{ success: boolean; message: string }>(`/topics/${id}`);
  //   } catch (error) {
  //     console.error(`Error deleting topic ${id}:`, error);
  //     throw error;
  //   }
  // }


  // async searchArticles(query: string, skip: number = 0, limit: number = 50): Promise<ArticlesData> {
  //   try {
  //     return await this.apiClient.get<ArticlesData>(
  //       `/topics/search?q=${encodeURIComponent(query)}&skip=${skip}&limit=${limit}`
  //     );
  //   } catch (error) {
  //     console.error(`Error searching topics with query "${query}":`, error);
  //     throw error;
  //   }
  // }
}

export const articlesService = new ArticlesService();

export default articlesService;