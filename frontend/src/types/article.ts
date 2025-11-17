import { Summary } from "./summary";
import { Topic } from "./topic";

export interface Article {
  id: number;
  title: string;
  url: string;
  content: string;
  source: string;
  author: string;
  published_at: string;
  image_url: string;
  is_processed: boolean;
  topic_id: number;
  created_at: string;
  updated_at: string;
                
  topic?: Topic;
  summary?: Summary;

  processing_error?: string;
  source_metadata?: any;
}

export interface SearchParams {
  content?: string;
  title?: string;
  publishedAfter?: string;
  publishedBefore?: string;
  source?: string;
  topic: Topic | null;
  sortBy?: 'relevance'
}