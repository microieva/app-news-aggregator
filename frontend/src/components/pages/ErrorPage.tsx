"use client"

import { useRouter } from "next/navigation";
import { ApiError } from "@/types";
import { AnimatedWrapper } from "../wrappers/AnimatedWrapper";

export const ErrorPage = ({error}: {error:ApiError}) => {
  const router = useRouter();

  return (
    <AnimatedWrapper>
      <div className="wrapper flex justify-center">
        <div className="text-center content-center font-foreground font-secondary">
          <p className="text-sm font-bold">{error.statusCode} - {error.message}</p>
          <p className="text-xs font-bold">{error.detail}</p>
          <div onClick={()=> router.refresh()} className="hover:opacity-70 mt-10 text-tertiary hover:cursor-pointer">
            <p className="xs">Try refreshing the page..</p>
            <img 
              src="/refresh.svg"
              alt="Refresh the page"
              className="w-10 h-10 m-auto mt-6"
            />
          </div>
        </div>
      </div>
    </AnimatedWrapper>
  )
}