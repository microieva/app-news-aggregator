"use client"

import { useRouter } from "next/navigation";
import { ApiError } from "@/types";
import { AnimatedWrapper } from "../wrappers/AnimatedWrapper";

export const ErrorPage = ({error}: {error:ApiError}) => {
  const router = useRouter();

  return (
    <AnimatedWrapper>
      <div className="wrapper flex justify-center">
        <div className="text-center content-center">
          <p>{error.statusCode} - {error.message}</p>
          <p><em>{error.detail}</em></p>
          <div onClick={()=> router.refresh()} className="hover:opacity-70 mt-10 text-gray-400 hover:cursor-pointer">
            <p>Try refreshing the page..</p>
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