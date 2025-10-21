import { useState, useCallback } from 'react';
import { topicsService } from '@/api/topics/service';
import { Topic, CreateTopicRequest, UpdateTopicRequest } from '@/types/topic';
import { ApiError } from '@/types/api';

export const useTopics = () => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<ApiError | null>(null);

  const getTopics = useCallback(async (): Promise<Topic[]> => {
    setLoading(true);
    setError(null);
    try {
      const response = await topicsService.getTopics();
      return response.data;
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError);
      throw apiError;
    } finally {
      setLoading(false);
    }
  }, []);

  const createTopic = useCallback(async (topicData: CreateTopicRequest): Promise<Topic> => {
    setLoading(true);
    setError(null);
    try {
      const response = await topicsService.createTopic(topicData);
      return response.data;
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError);
      throw apiError;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateTopic = useCallback(async (id: string, topicData: UpdateTopicRequest): Promise<Topic> => {
    setLoading(true);
    setError(null);
    try {
      const response = await topicsService.updateTopic(id, topicData);
      return response.data;
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError);
      throw apiError;
    } finally {
      setLoading(false);
    }
  }, []);

  const patchTopic = useCallback(async (id: string, topicData: Partial<UpdateTopicRequest>): Promise<Topic> => {
    setLoading(true);
    setError(null);
    try {
      const response = await topicsService.patchTopic(id, topicData);
      return response.data;
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError);
      throw apiError;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteTopic = useCallback(async (id: string): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      await topicsService.deleteTopic(id);
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError);
      throw apiError;
    } finally {
      setLoading(false);
    }
  }, []);

  const toggleTopicStatus = useCallback(async (id: string): Promise<Topic> => {
    setLoading(true);
    setError(null);
    try {
      const response = await topicsService.toggleTopicStatus(id);
      return response.data;
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError);
      throw apiError;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    getTopics,
    createTopic,
    updateTopic,
    patchTopic,
    deleteTopic,
    toggleTopicStatus,
  };
};