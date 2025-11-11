import { ApiResponse, TopicsData } from '@/types/api';
import { apiClient } from '@/utils/client';

export const topicsService = {

  async getTopics(skip: number = 0, limit: number = 100): Promise<TopicsData> {
    try {
      const response =  await apiClient.get<ApiResponse<TopicsData>>(`/topics?skip=${skip}&limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching topics:', error);
      throw error;
    }
  },

  async getUsedTopics(source?: string, skip: number = 0, limit: number = 100 ): Promise<TopicsData> {
    const config = source ? { params: { source } } : undefined;
    try {
      const response =  await apiClient.get<ApiResponse<TopicsData>>(`/topics/used`, config);
      return response.data;
    } catch (error) {
      console.error('Error fetching used topics:', error);
      throw error;
    }
  }

}