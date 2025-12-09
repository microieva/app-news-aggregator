import Link from "next/link"

export const PageFooter = () => {
  return (
    <div className="border-t-[1px] border-[var(--np-color-primary)] w-full">
      <div className="grid grid-cols-3 grid-rows-2 w-full px-1 md:px-4 gap-y-0 my-4 font-secondary min-h-max" >
        <p className="text-gray-500 text-start text-xs">Developer</p>
        <p className="text-gray-500 text-center text-xs">Layout Design</p>
        <p className="text-gray-500 text-end text-xs">Contact</p>

        <p className="text-start text-xs">Ieva Vyliaudaite</p>
        <Link href="" target="_blank" className="text-center text-xs hover:font-bold hover:cursor-pointer duration-300">Paperio, David Satria</Link>
        <p className="text-end text-xs">ieva.vyliaudaite@me.com</p>
      </div>
      <div className="text-center font-primary mx-auto font-bold">
        <h1 className="text-2xl">News Paper</h1>
      </div>
    </div>
  )
}