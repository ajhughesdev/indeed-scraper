import { useEffect, useRef, useState } from 'react'

const Favorites = ({ visible, children }) => {
  const [isVisible, setIsVisible] = useState(false)
  const dialog = useRef(null)

  useEffect(() => {
    if (visible !== isVisible) {
      setIsVisible(visible)
      if (visible && !dialog.current.open) {
        dialog.current.showModal()
      } else if (!visible && dialog.current.open) {
        dialog.current.close()
      }
    }
  }, [visible, isVisible])

  return (
    <dialog
      className='modal'
      ref={dialog}
    >

      <h2>Favorites</h2>
      {children}
    </dialog>
  )
}

export default Favorites
