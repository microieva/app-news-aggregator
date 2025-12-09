import { AnimatedWrapper } from "../wrappers/AnimatedWrapper"

export const LoadingPage = ({text}:{text?:string}) => {
  return (
    <AnimatedWrapper>
      <div className="wrapper content-center">
        <div className="text-center text-foreground">
          <div className="loading loading-spinner"></div>
          {text && <p className="text-sm font-bold">{text}</p>}
        </div>
      </div>
    </AnimatedWrapper>
  )
}