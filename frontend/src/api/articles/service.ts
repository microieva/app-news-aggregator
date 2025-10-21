import { apiClient } from '@/api/client';
//import { Topic, CreateTopicRequest, UpdateTopicRequest } from '@/types/topic';
import { ApiResponse, PaginatedResponse } from '@/types/api';

export const articlesService = {
  async getArticles(): Promise<ApiResponse<any[]>> {
    return apiClient.get<any[]>('/articles');
  },

  // async getTopicsPaginated(page: number = 1, limit: number = 10): Promise<ApiResponse<PaginatedResponse<Topic>>> {
  //   return apiClient.get<PaginatedResponse<Topic>>(`/topics?page=${page}&limit=${limit}`);
  // },

  // async getTopicById(id: string): Promise<ApiResponse<Topic>> {
  //   return apiClient.get<Topic>(`/topics/${id}`);
  // },

  // async createTopic(topicData: CreateTopicRequest): Promise<ApiResponse<Topic>> {
  //   return apiClient.post<Topic>('/topics', topicData);
  // },

  // async updateTopic(id: string, topicData: UpdateTopicRequest): Promise<ApiResponse<Topic>> {
  //   return apiClient.put<Topic>(`/topics/${id}`, topicData);
  // },

  // async patchTopic(id: string, topicData: Partial<UpdateTopicRequest>): Promise<ApiResponse<Topic>> {
  //   return apiClient.patch<Topic>(`/topics/${id}`, topicData);
  // },

  // async deleteTopic(id: string): Promise<ApiResponse<void>> {
  //   return apiClient.delete<void>(`/topics/${id}`);
  // },

  // async toggleTopicStatus(id: string): Promise<ApiResponse<Topic>> {
  //   return apiClient.patch<Topic>(`/topics/${id}/toggle`);
  // },

  // async toggleTopicActive(id: string, isActive: boolean): Promise<ApiResponse<Topic>> {
  //   return apiClient.patch<Topic>(`/topics/${id}`, { isActive });
  // },
};