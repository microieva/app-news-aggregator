import { usePage } from "@/contexts/PageContext";
import { useState } from "react";

export const Dropdown = ({options}: {options:string[]}) =>{
  const { source, setSource } = usePage();
  const [open, setOpen] = useState<boolean>(false);

  const handleSelect =(option:string)=> {
    setSource(option);
    setOpen(false);
  }

  return (
    <div className="dropdown dropdown-hover w-full">
      <div onClick={()=> {setOpen(true)}} tabIndex={0} role="button" className="flex bg-[var(--np-background)] content-center items-center justify-between px-4 py-2">
          {source ? <p className="text-sm">source: {source}</p> : <p className="text-sm">source</p>}
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="h-6">
          <path fillRule="evenodd" d="M5.22 8.22a.75.75 0 0 1 1.06 0L10 11.94l3.72-3.72a.75.75 0 1 1 1.06 1.06l-4.25 4.25a.75.75 0 0 1-1.06 0L5.22 9.28a.75.75 0 0 1 0-1.06Z" clipRule="evenodd" />
        </svg>
      </div>
      {open && <ul tabIndex={0} className="dropdown-content menu z-50 w-52 shadow bg-[var(--np-color-primary)] text-[var(--np-background)] rounded-md border border-[var(--np-color-primary)]">
        {options.map((option:string) => 
          <li onClick={()=>handleSelect(option)}><a>{option}</a></li>
        )}
      </ul>}
    </div>
  )
}