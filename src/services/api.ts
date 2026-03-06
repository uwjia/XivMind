export { apiRequest } from '@/services/common'
export type { MessageResponse } from '@/services/common'

export { bookmarkAPI } from '@/services/bookmark'
export type { BookmarkData, Bookmark, BookmarkListResponse } from '@/services/bookmark'

export { downloadAPI } from '@/services/download'
export type { DownloadTaskData, DownloadTask, DownloadTaskListResponse } from '@/services/download'

import { bookmarkAPI } from '@/services/bookmark'
import { downloadAPI } from '@/services/download'

export const apiService = {
  addBookmark: bookmarkAPI.add,
  removeBookmark: bookmarkAPI.remove,
  checkBookmark: bookmarkAPI.check,
  checkBookmarkBatch: bookmarkAPI.checkBatch,
  getBookmarks: bookmarkAPI.list,
  searchBookmarks: bookmarkAPI.search,
  
  createDownloadTask: downloadAPI.create,
  getDownloadTasks: downloadAPI.list,
  getDownloadTask: downloadAPI.get,
  deleteDownloadTask: downloadAPI.delete,
  retryDownloadTask: downloadAPI.retry,
  cancelDownloadTask: downloadAPI.cancel,
  openDownloadFile: downloadAPI.openFile,
}
