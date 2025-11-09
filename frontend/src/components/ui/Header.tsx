import { Topic } from "@/types/topic";
import { useRouter } from 'next/router';
import { DateTime } from "luxon";
import clsx from "clsx";
import { Dropdown } from "./Dropdown";
import { usePage } from "@/contexts/PageContext";
import { useHeader } from "@/contexts/HeaderContext";
import { useEffect } from "react";
import { useArticles } from "@/contexts/ArticlesContext";

export const Header = () => {
  
  const { sources, topics, loading, error, refreshTopicsWithSource } = useHeader();
  const { source, topic, setTopic, setHomePage } = usePage();
  const router = useRouter();
  const date = DateTime.now();

  useEffect(()=> {
    if (source) refreshTopicsWithSource(source);
  }, [source ])

  const handlePageChange = (topic:Topic, route:string) => {
    setTopic(topic);
    router.push(`/${route}`);
  }

  const goHome = () => {
    router.push('/');
    setHomePage();
  }

  if (error) return (
    <header className="bg-[var(--np-background)] border-b-2">
      <div className="m-auto">
        <div className="text-center">
          <p>Error: {error.statusCode} - {error.message}</p>
          <p><em>{error.detail}</em></p>
        </div>
      </div>
    </header>
  );

  if (loading) {
    return (
      <header className="bg-[var(--np-background)] border-b-2">
        <div className="container m-auto">
          <div className="text-center">Loading header...</div>
        </div>
      </header>
    );
  } else {
    return (
      <header className="bg-[var(--np-background)] border-b-2">
        <div className="grid-header-top">
          <div className="grid-gap grid grid-cols-[1fr_5fr_1fr] grid-rows-1 items-center bg-[var(--np-color-primary)] w-full border-b border-[var(--np-color-primary)]-100">
          
            <div className="flex flex-row bg-[var(--np-foreground)] rounded-br-md h-full items-center pl-4">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="h-6">
                  <path d="M16.555 5.412a8.028 8.028 0 0 0-3.503-2.81 14.899 14.899 0 0 1 1.663 4.472 8.547 8.547 0 0 0 1.84-1.662ZM13.326 7.825a13.43 13.43 0 0 0-2.413-5.773 8.087 8.087 0 0 0-1.826 0 13.43 13.43 0 0 0-2.413 5.773A8.473 8.473 0 0 0 10 8.5c1.18 0 2.304-.24 3.326-.675ZM6.514 9.376A9.98 9.98 0 0 0 10 10c1.226 0 2.4-.22 3.486-.624a13.54 13.54 0 0 1-.351 3.759A13.54 13.54 0 0 1 10 13.5c-1.079 0-2.128-.127-3.134-.366a13.538 13.538 0 0 1-.352-3.758ZM5.285 7.074a14.9 14.9 0 0 1 1.663-4.471 8.028 8.028 0 0 0-3.503 2.81c.529.638 1.149 1.199 1.84 1.66ZM17.334 6.798a7.973 7.973 0 0 1 .614 4.115 13.47 13.47 0 0 1-3.178 1.72 15.093 15.093 0 0 0 .174-3.939 10.043 10.043 0 0 0 2.39-1.896ZM2.666 6.798a10.042 10.042 0 0 0 2.39 1.896 15.196 15.196 0 0 0 .174 3.94 13.472 13.472 0 0 1-3.178-1.72 7.973 7.973 0 0 1 .615-4.115ZM10 15c.898 0 1.778-.079 2.633-.23a13.473 13.473 0 0 1-1.72 3.178 8.099 8.099 0 0 1-1.826 0 13.47 13.47 0 0 1-1.72-3.178c.855.151 1.735.23 2.633.23ZM14.357 14.357a14.912 14.912 0 0 1-1.305 3.04 8.027 8.027 0 0 0 4.345-4.345c-.953.542-1.971.981-3.04 1.305ZM6.948 17.397a8.027 8.027 0 0 1-4.345-4.345c.953.542 1.971.981 3.04 1.305a14.912 14.912 0 0 0 1.305 3.04Z" />
                </svg>
              <div className="flex flex-col px-4">
                <p className="font-bold text-extrasmall"> 
                  {date.toFormat('d MMM, yyyy')}
                </p>
                <p className="text-gray-600 text-extrasmall">{date.toFormat('HH:mm a, cccc')}</p>

              </div>
            </div>
            
            <div className="rounded-bl-md rounded-br-md bg-[var(--np-background)] py-8 text-center">
              <a 
                href="/"
                className="text-7xl font-bold text-gray-800 hover:text-gray-600"
              >
                <h1 className="font-primary h-full">News Aggregator</h1>
              </a>
            </div>
            
            <div className="flex justify-end rounded-bl-md bg-[var(--np-background)] h-full">
              <button 
                onClick={() => goHome()}
                className="text-gray-600 hover:text-gray-900"
              >
                
              </button>
            </div>
          </div>
        </div>
        <div className="grid-header-bottom">
          <div className="row-start-1 col-start-1 flex items-center bg-[var(--np-background)] rounded-br-md">
            <Dropdown options={sources} />
          </div>
          <div className="row-start-1 col-start-2 rounded-bl-md rounded-tr-md bg-[var(--np-background)] overflow-hidden">
            <div className="overflow-x-auto scrollbar-hide h-full">
              <div 
                role="tablist" 
                className={clsx(
                  'tabs tabs-lift tabs-lg flex whitespace-nowrap min-w-max space-x-1 tabs-no-border h-full transition-colors duration-300',
                  {'text-[var(--np-color-primary)]':!topic}
                )}
              >
                {topics?.map((t: Topic, i) => {
                  const route = t.name.replace(/ /g, '-');
                  const isActive = router.asPath.endsWith(`/${route}/`);
                  return (
                    <button 
                      key={t.name}
                      role="tab" 
                      onClick={() => handlePageChange(t, route)}
                      className={clsx(
                        'tab tab-lifted h-full flex-shrink-0 transition-colors duration-200 focus:tab-active hover:tab-active',
                        {
                          'tab-active ': isActive,
                          'non-active-hover':!isActive,
                          'text-[var(--np-color-primary)]': !topic // no topic equals initial state
                        }
                      )}
                    >
                      {t.name}
                    </button>  
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </header>
    )
  }    
}