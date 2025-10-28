export interface Summary {
  id: number
  article_id: number;
  content: string;
  model_name: string;
  quality_level: string;
  word_count: number;
  char_count:number
  processing_time_ms: number
  is_successful: boolean
  status: string;
  created_at: string;
}