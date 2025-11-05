export const FrontPageFooter = () => {
  return (
    <div className="border-t-[1px] border-[var(--np-color-primary)] w-full">
          <div className="grid grid-cols-3 grid-rows-2 w-full px-4 gap-y-1 my-4 font-secondary">
            <div className="text-gray-500 text-start text-xs">
              <p>Developer</p>
            </div>
            <div className="text-gray-500 text-center text-xs">
              <p>Layout Design By</p>
            </div>
            <div className="text-gray-500 text-end text-xs">
              <p>Contact</p>
            </div>
            
            <div className="text-start text-md">
              <p>Ieva Vyliaudaite</p>
            </div>
            <div className="text-center text-md">
              <p>Paperio, Dribble</p>
            </div>
            <div className="text-end text-md">
              <p>ieva.vyliaudaite@me.com</p>
            </div>
          </div>
          <h1 className="text-9xl mx-auto my-4">News Paper</h1>
        </div>
  )
}