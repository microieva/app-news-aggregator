import _ from 'lodash';
import clsx from "clsx";
import { useState } from "react";
import { useArticles } from "@/contexts/ArticlesContext";
import { useHeader } from "@/contexts/HeaderContext";
import { usePage } from '@/contexts/PageContext';
import { SearchParams, Topic } from "@/types";

export const AdvancedSearchForm = () => {
  const { clearSearch, loading, searchParams, performSearch, setIsSearchOpen } = useArticles();
  const { sources, topics } = useHeader();
  const { topic, source } = usePage();

  const [formValues, setFormValues] = useState<SearchParams>({ 
    content:searchParams?.content ||  '',
    title: searchParams?.title || '',
    publishedAfter: searchParams?.publishedAfter || '',
    publishedBefore: searchParams?.publishedBefore || '',
    source: searchParams?.source || '',
    topic: searchParams?.topic || null,
    sortBy: searchParams?.sortBy || 'relevance'
  });

  const isFormEmpty = () => _.isEmpty(_.pickBy(formValues, value => 
    value !== '' && value !== 'relevance'
  ));

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    const topic = topics.find(topic => topic.name === value)
    setFormValues(prev => ({
      ...prev,
      [name]: name === 'topic' ? topic : value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    let topicId = formValues.topic?.id || topic?.id;
    const searchTopic: Topic | null = topics.find(topic => topic.id === topicId) || null;
    performSearch({...formValues, topic:searchTopic});
  };

  const handleReset = () => {
    setFormValues({
      content: '',
      title: '',
      publishedAfter: '',
      publishedBefore: '',
      source: '',
      topic: null,
      sortBy: 'relevance'
    });
    clearSearch();
    setIsSearchOpen(true);
  };

  return (
    <form className="space-y-2" onSubmit={handleSubmit} >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Title Search */}
        <div className="form-control">
          <label className="label">
            <span className="label-text font-semibold">Search in Titles</span>
          </label>
          <input
            type="text"
            name="title"
            value={formValues.title}
            onChange={handleInputChange}
            placeholder="Enter keywords to search in article titles..."
            className={clsx(
              "placeholder:text-[var(--np-foreground)] input input-sm input-bordered border-[var(--np-color-primary)] w-full focus:border-[var(--np-foreground)] rounded-md",
              {
                "bg-[var(--np-foreground)]": formValues.title !== '',
                "bg-[var(--np-background)]": formValues.title === ''
              }
            )}
          />
        </div>
        {/* Content Search */}
        <div className="form-control">
          <label className="label">
            <span className="label-text font-semibold">Search in Content</span>
          </label>
          <input
            name="content"
            value={formValues.content}
            onChange={handleInputChange}
            type="text"
            placeholder="Enter keywords to search in article content..."
            className={clsx(
              "placeholder:text-[var(--np-foreground)] input input-sm input-bordered border-[var(--np-color-primary)] w-full focus:border-[var(--np-foreground)] rounded-md",
              {
                "bg-[var(--np-foreground)]": formValues.content !== '',
                "bg-[var(--np-background)]": formValues.content === ''
              }
            )}
          />
        </div>
      </div>
      {/* Date Range */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="form-control">
          <label className="label">
            <span className="label-text font-semibold">Published After</span>
          </label>
          <input
            name="publishedAfter"
            value={formValues.publishedAfter}
            onChange={handleInputChange}
            type="date"
            className={clsx(
              "placeholder:text-[var(--np-foreground)] input input-sm input-bordered border-[var(--np-color-primary)] w-full focus:border-[var(--np-foreground)] rounded-md",
              {
                "bg-[var(--np-foreground)]": formValues.publishedAfter !== '',
                "bg-[var(--np-background)]": formValues.publishedAfter === ''
              }
            )}
          />
        </div>

        <div className="form-control">
          <label className="label">
            <span className="label-text font-semibold">Published Before</span>
          </label>
          <input
            name="publishedBefore"
            value={formValues.publishedBefore}
            onChange={handleInputChange}
            type="date"
            className={clsx(
              "placeholder:text-[var(--np-foreground)] input input-sm input-bordered border-[var(--np-color-primary)] w-full focus:border-[var(--np-foreground)] rounded-md",
              {
                "bg-[var(--np-foreground)]": formValues.publishedBefore !== '',
                "bg-[var(--np-background)]": formValues.publishedBefore === ''
              }
            )}
          />
        </div>
      </div>

      {/* Additional Filters */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="form-control">
          <label className="label">
            <span className="label-text font-semibold">Source</span>
          </label>
          <select 
            name="source"
            value={source || formValues.source}
            onChange={handleInputChange}
            disabled={Boolean(source)}
            className={clsx(
              "placeholder:text-[var(--np-foreground)] select select-sm select-bordered border-[var(--np-color-primary)] w-full focus:border-[var(--np-foreground)] rounded-md disabled:bg-[var(--np-foreground)] disabled:border-gray-600",
              {
                "bg-[var(--np-foreground)]": formValues.source !== '' || source,
                "bg-[var(--np-background)]": formValues.source === ''
              }
            )}
          >
            <option value="">All Sources</option>
            {sources.map((option: string) => 
              <option key={option} value={option}>
                {option}
              </option>
            )}
          </select>
        </div>

        <div className="form-control">
          <label className="label">
            <span className="label-text font-semibold">Topic</span>
          </label>
          <select 
            name="topic"
            value={formValues.topic?.name || topic?.name || ''}
            onChange={handleInputChange}
            className={clsx(
              "placeholder:text-[var(--np-foreground)] select select-sm select-bordered border-[var(--np-color-primary)] w-full focus:border-[var(--np-foreground)] rounded-md",
              {
                "bg-[var(--np-foreground)]": (formValues.topic as Topic)?.name || topic?.name,
                "bg-[var(--np-background)]": !formValues.topic
              }
            )}
          >
            <option value="">All Topics</option>
            {topics.map((option: Topic) => 
              <option key={option.id} value={option.name}>
                {option.name}
              </option>
            )}
          </select>
        </div>
      </div>
      <div className="form-control">
        <label className="label">
          <span className="label-text font-semibold">Sort By</span>
        </label>
        <select 
          name="sortBy"
          value={formValues.sortBy}
          onChange={handleInputChange}
          className={clsx(
            "placeholder:text-[var(--np-foreground)] select select-sm select-bordered border-[var(--np-color-primary)] w-full focus:border-[var(--np-foreground)] rounded-md",
            {
              "bg-[var(--np-foreground)]": formValues.sortBy !== 'relevance',
              "bg-[var(--np-background)]": formValues.sortBy === 'relevance'
            }
          )}
        >
          <option value="relevance">Relevance</option>
          <option value="newest">Newest First</option>
          <option value="oldest">Oldest First</option>
          <option value="title_asc">Title A-Z</option>
          <option value="title_desc">Title Z-A</option>
        </select>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-3 pt-4">
        <button
          disabled={isFormEmpty()}
          type="submit"
          className="btn btn-sm bg-[var(--np-foreground)] flex-1 sm:flex-none border-none text-gray-600 hover:bg-inherit"
        >
          {loading ? 
          <>
            <span className="loading loading-spinner w-4 h-4"></span>
            <span>Searching..</span>
          </> 
          : 
          <>
            <img src="/search.svg" className="w-4 h-4"  />
            <span>Search</span>
          </>}
        </button>
        
        <button
          disabled={!formValues}
          type="reset"
          className="btn btn-ghost flex-1 sm:flex-none btn-sm"
          onClick={handleReset}
        >
          Reset
        </button>
        
        <button
          onClick={()=>clearSearch()}
          type="button"
          className="btn bg-[var(--np-background)] border-transparent flex-1 sm:flex-none btn-sm hover:bg-[var(--np-foreground)] hover:text-gray-600"
        >
          Close
        </button>
      </div>
    </form>
  )
}