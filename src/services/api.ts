export { apiRequest } from './common'
export type { MessageResponse } from './common'

export { bookmarkAPI } from './bookmark'
export type { BookmarkData, Bookmark, BookmarkListResponse } from './bookmark'

export { downloadAPI } from './download'
export type { DownloadTaskData, DownloadTask, DownloadTaskListResponse } from './download'

import { bookmarkAPI } from './bookmark'
import { downloadAPI } from './download'

export const apiService = {
  addBookmark: bookmarkAPI.add,
  removeBookmark: bookmarkAPI.remove,
  checkBookmark: bookmarkAPI.check,
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
