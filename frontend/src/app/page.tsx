import { Articles } from "@/components/ui/Articles";

export default function Home() {
  return (
    <main className="flex-1 container mx-auto px-4 py-8">
      <div className="text-center max-w-2xl mx-auto">
        <h1 className="text-4xl font-bold tracking-tight mb-6">
          News Aggregator
        </h1>
        <p className="text-xl text-muted-foreground mb-8">
          Your personalized news dashboard powered by Next.js 15
        </p>
        <div className="p-6 bg-card rounded-lg border shadow-sm">
          <div className="flex items-center justify-center mb-4">
            <div className="flex gap-2">
              <div className="px-3 py-1 bg-primary text-primary-foreground rounded-full text-sm font-medium">
                Next.js 15
              </div>
              <div className="px-3 py-1 bg-secondary text-secondary-foreground rounded-full text-sm font-medium">
                React 19
              </div>
              <div className="px-3 py-1 bg-secondary text-secondary-foreground rounded-full text-sm font-medium">
                Tailwind CSS 4
              </div>
            </div>
          </div>
          <p className="text-card-foreground">
            Frontend setup completed successfully! Ready for topic management implementation.
          </p>
        </div>
        <div className="p-6 bg-card rounded-lg border shadow-sm mt-4">
          <div className="flex items-center justify-center my-4 text-card-foreground">
            <Articles />
          </div>
        </div>
      </div>
    </main>
  )
}