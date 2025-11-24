import { AnimatedWrapper } from "../wrappers/AnimatedWrapper"

export const LoadingPage = ({text}:{text?:string}) => {
  return (
    <AnimatedWrapper>
      <div className="wrapper content-center">
        <div className="text-center text-[var(--np-foreground)]">
          <div className="loading loading-spinner"></div>
          {text && <p>{text}</p>}
        </div>
      </div>
    </AnimatedWrapper>
  )
}