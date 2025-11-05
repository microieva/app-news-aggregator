import { ApiResponse, TopicsData } from '@/types/api';
import { ApiClient } from '@/utils/client';

class TopicsService {
  private apiClient: ApiClient;

  constructor() {
    this.apiClient = new ApiClient(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api');
  }

  async getTopics(skip: number = 0, limit: number = 100): Promise<TopicsData> {
    try {
      return await this.apiClient.get<TopicsData>(`/topics?skip=${skip}&limit=${limit}`);
    } catch (error) {
      console.error('Error fetching topics:', error);
      throw error;
    }
  }

  async getUsedTopics(skip: number = 0, limit: number = 100): Promise<TopicsData> {
    const topics = localStorage.getItem('usedTopics') || undefined;
    if (topics) {
      return { topics: JSON.parse(topics) , total: JSON.parse(topics).length };
    } else {
      try {
        const data = await this.apiClient.get<TopicsData>(`/topics/used`);
        localStorage.setItem('usedTopics', JSON.stringify(data.topics));
        return data;
      } catch (error) {
        console.error('Error fetching used topics:', error);
        throw error;
      }
    }
  }

  // async getTopicById(id: string): Promise<{ data: Topic }> {
  //   try {
  //     return await this.apiClient.get<{ data: Topic }>(`topics/${id}`);
  //   } catch (error) {
  //     console.error(`Error fetching topic ${id}:`, error);
  //     throw error;
  //   }
  // }

  // async getTopicByName(name: string): Promise<{ data: Topic }> {
  //   try {
  //     return await this.apiClient.get<{ data: Topic }>(`/topics/name/${encodeURIComponent(name)}`);
  //   } catch (error) {
  //     console.error(`Error fetching topic by name ${name}:`, error);
  //     throw error;
  //   }
  // }

  /**
   * Create a new topic
   */
  // async createTopic(topicData: Omit<Topic, 'id' | 'created_at' | 'updated_at'>): Promise<{ data: Topic }> {
  //   try {
  //     return await this.apiClient.post<{ data: Topic }>('/topics', topicData);
  //   } catch (error) {
  //     console.error('Error creating topic:', error);
  //     throw error;
  //   }
  // }

  /**
   * Update an existing topic
   */
  // async updateTopic(id: string, topicData: Partial<Topic>): Promise<{ data: Topic }> {
  //   try {
  //     return await this.apiClient.put<{ data: Topic }>(`/topics/${id}`, topicData);
  //   } catch (error) {
  //     console.error(`Error updating topic ${id}:`, error);
  //     throw error;
  //   }
  // }

  /**
   * Delete a topic
   */
  // async deleteTopic(id: string): Promise<{ success: boolean; message: string }> {
  //   try {
  //     return await this.apiClient.delete<{ success: boolean; message: string }>(`/topics/${id}`);
  //   } catch (error) {
  //     console.error(`Error deleting topic ${id}:`, error);
  //     throw error;
  //   }
  // }

  // async getTopicsCount(): Promise<{ data: { count: number } }> {
  //   try {
  //     return await this.apiClient.get<{ data: { count: number } }>('/topics/count');
  //   } catch (error) {
  //     console.error('Error fetching topics count:', error);
  //     throw error;
  //   }
  // }

  // async getUsedTopicsCount(): Promise<{ data: { count: number } }> {
  //   try {
  //     return await this.apiClient.get<{ data: { count: number } }>('/topics/used/count');
  //   } catch (error) {
  //     console.error('Error fetching used topics count:', error);
  //     throw error;
  //   }
  // }

  // async searchTopics(query: string, skip: number = 0, limit: number = 50): Promise<TopicsResponse> {
  //   try {
  //     return await this.apiClient.get<TopicsResponse>(
  //       `/topics/search?q=${encodeURIComponent(query)}&skip=${skip}&limit=${limit}`
  //     );
  //   } catch (error) {
  //     console.error(`Error searching topics with query "${query}":`, error);
  //     throw error;
  //   }
  // }
}

export const topicsService = new TopicsService();

//export default topicsService;