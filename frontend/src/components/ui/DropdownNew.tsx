import { useState } from "react";

export const DropdownNew = (
  {
    options, 
    handleSelect, 
    selected,
    children
  }: {
    options:string[], 
    handleSelect:(option:string)=>void,  
    selected?:string,
    children:React.ReactNode
  }) =>{
  const [open, setOpen] = useState<boolean>(false);

  return (
    <div className="dropdown dropdown-hover w-full dropdown-end relative">
      <div
        onClick={()=> setOpen(!open)} 
        tabIndex={0} 
        role="button" 
      >
        {children}
      </div>
      {open && 
        <ul tabIndex={0} className="dropdown-content menu w-52 shadow bg-[var(--np-color-primary)] text-background rounded-md border border-[var(--np-color-primary)] absolute left-0 mt-2 z-50">
          {options.map((option:string) => 
            <li 
              className={option === selected ? "bg-background text-primary" : ""}
              key={option} 
              onClick={()=>{handleSelect(option); setOpen(false)}}>
                <a>{option}</a>
            </li>
          )}
        </ul>}
    </div>
  )
}