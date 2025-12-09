export const Footer = () => {
  return (
    <footer className="w-full bg-background">
      <div className="grid grid-cols-[25%,75%] md:grid-cols-[15%,85%] grid-rows-1 bg-[var(--np-color-primary)] grid-gap">
        <div className="bg-background rounded-tr-md flex flex-row p-2 gap-4">
          <a className="w-8">
            <img src="linkedin.png" className="h-8"/>
          </a>
          <a className="w-8">
            <img src="github.png" className="h-8 "/>
          </a>
        </div>
        <div className="bg-background rounded-tl-md flex flex-row p-2 justify-end">
          <p className="content-center text-xs">&copy; {new Date().getFullYear()} News Aggregator. Ieva Vyliaudaite.</p>
        </div>
      </div>
    </footer>
  );
}