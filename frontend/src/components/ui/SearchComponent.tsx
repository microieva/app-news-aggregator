import { AnimatePresence, motion } from "framer-motion"

export const SearchComponent = () => {
  return (
    <AnimatePresence>
          <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.5, ease: 'easeInOut' }}
          className="overflow-hidden"
        >
      <div className="border-b border-t-2 h-48">search div</div>
    </motion.div>
  </AnimatePresence>
  )
}