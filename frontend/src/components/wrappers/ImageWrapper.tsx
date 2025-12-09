export const ImageWrapper = ({url, title, classNames}:{url:string, title:string, classNames:string[]}) => {
  return (
     <div className={`bg-background aspect-[16/9] max-h-[50vh] overflow-hidden w-full ${classNames}`}>
      <img 
        src={url} 
        alt={title} 
        className="w-full h-full object-cover object-center mt-4 opacity-70"
      />
    </div>
  )
}