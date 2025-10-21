import { useState, useCallback } from 'react';
import { articlesService } from '@/api/articles/service';
//import { Article, CreateArticleRequest, UpdateArticleRequest } from '@/types/article';
import { ApiError } from '@/types/api';

export const useArticles = () => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<ApiError | null>(null);

  const getArticles = useCallback(async (): Promise<any[]> => {
    setLoading(true);
    setError(null);
    try {
      const response = await articlesService.getArticles();
      return response.data;
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError);
      throw apiError;
    } finally {
      setLoading(false);
    }
  }, []);

  // const createArticle = useCallback(async (ArticleData: CreateArticleRequest): Promise<Article> => {
  //   setLoading(true);
  //   setError(null);
  //   try {
  //     const response = await articlesService.createArticle(ArticleData);
  //     return response.data;
  //   } catch (err) {
  //     const apiError = err as ApiError;
  //     setError(apiError);
  //     throw apiError;
  //   } finally {
  //     setLoading(false);
  //   }
  // }, []);

  // const updateArticle = useCallback(async (id: string, ArticleData: UpdateArticleRequest): Promise<Article> => {
  //   setLoading(true);
  //   setError(null);
  //   try {
  //     const response = await articlesService.updateArticle(id, ArticleData);
  //     return response.data;
  //   } catch (err) {
  //     const apiError = err as ApiError;
  //     setError(apiError);
  //     throw apiError;
  //   } finally {
  //     setLoading(false);
  //   }
  // }, []);

  // const patchArticle = useCallback(async (id: string, ArticleData: Partial<UpdateArticleRequest>): Promise<Article> => {
  //   setLoading(true);
  //   setError(null);
  //   try {
  //     const response = await articlesService.patchArticle(id, ArticleData);
  //     return response.data;
  //   } catch (err) {
  //     const apiError = err as ApiError;
  //     setError(apiError);
  //     throw apiError;
  //   } finally {
  //     setLoading(false);
  //   }
  // }, []);

  // const deleteArticle = useCallback(async (id: string): Promise<void> => {
  //   setLoading(true);
  //   setError(null);
  //   try {
  //     await articlesService.deleteArticle(id);
  //   } catch (err) {
  //     const apiError = err as ApiError;
  //     setError(apiError);
  //     throw apiError;
  //   } finally {
  //     setLoading(false);
  //   }
  // }, []);

  // const toggleArticlestatus = useCallback(async (id: string): Promise<Article> => {
  //   setLoading(true);
  //   setError(null);
  //   try {
  //     const response = await articlesService.toggleArticlestatus(id);
  //     return response.data;
  //   } catch (err) {
  //     const apiError = err as ApiError;
  //     setError(apiError);
  //     throw apiError;
  //   } finally {
  //     setLoading(false);
  //   }
  // }, []);

  return {
    loading,
    error,
    getArticles,
    // createArticle,
    // updateArticle,
    // patchArticle,
    // deleteArticle,
    // toggleArticlestatus,
  };
};