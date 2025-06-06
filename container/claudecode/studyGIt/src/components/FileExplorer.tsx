"use client";

import { useState } from 'react';
import styles from './FileExplorer.module.css';

interface FileExplorerProps {
  files: Record<string, string>;
  onFileOperation: (operation: string, data: { name: string; content: string }) => void;
}

export default function FileExplorer({ files, onFileOperation }: FileExplorerProps) {
  const [newFileName, setNewFileName] = useState('');
  const [newFileContent, setNewFileContent] = useState('');
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [editContent, setEditContent] = useState('');
  
  const handleCreateFile = () => {
    if (newFileName.trim() === '') return;
    
    onFileOperation('add', {
      name: newFileName,
      content: newFileContent || `// ${newFileName} の内容`
    });
    
    // Reset form
    setNewFileName('');
    setNewFileContent('');
  };
  
  const handleSelectFile = (fileName: string) => {
    setSelectedFile(fileName);
    setEditContent(files[fileName]);
  };
  
  const handleUpdateFile = () => {
    if (!selectedFile) return;
    
    onFileOperation('modify', {
      name: selectedFile,
      content: editContent
    });
    
    // Reset selection
    setSelectedFile(null);
  };
  
  const handleDeleteFile = () => {
    if (!selectedFile) return;
    
    onFileOperation('delete', {
      name: selectedFile,
      content: ''
    });
    
    // Reset selection
    setSelectedFile(null);
  };
  
  return (
    <div className={styles.fileExplorer}>
      <div className={styles.createFile}>
        <h2>新しいファイルを作成</h2>
        <div className={styles.formGroup}>
          <label htmlFor="fileName">ファイル名:</label>
          <input
            id="fileName"
            type="text"
            value={newFileName}
            onChange={(e) => setNewFileName(e.target.value)}
            placeholder="例: index.js"
          />
        </div>
        <div className={styles.formGroup}>
          <label htmlFor="fileContent">内容:</label>
          <textarea
            id="fileContent"
            value={newFileContent}
            onChange={(e) => setNewFileContent(e.target.value)}
            placeholder="ファイルの内容を入力してください"
            rows={5}
          />
        </div>
        <button className={styles.createButton} onClick={handleCreateFile}>
          ファイルを作成
        </button>
      </div>
      
      <div className={styles.filesList}>
        <h2>リポジトリ内のファイル</h2>
        {Object.keys(files).length === 0 ? (
          <p className={styles.emptyState}>まだファイルがありません。新しいファイルを作成してください。</p>
        ) : (
          <div className={styles.files}>
            {Object.keys(files).map((fileName) => (
              <div
                key={fileName}
                className={`${styles.file} ${selectedFile === fileName ? styles.selected : ''}`}
                onClick={() => handleSelectFile(fileName)}
              >
                <div className={styles.fileIcon}>📄</div>
                <div className={styles.fileName}>{fileName}</div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {selectedFile && (
        <div className={styles.editFile}>
          <h2>{selectedFile} を編集</h2>
          <textarea
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            className={styles.editContent}
            rows={10}
          />
          <div className={styles.actions}>
            <button className={styles.saveButton} onClick={handleUpdateFile}>
              保存
            </button>
            <button className={styles.deleteButton} onClick={handleDeleteFile}>
              削除
            </button>
            <button 
              className={styles.cancelButton} 
              onClick={() => setSelectedFile(null)}
            >
              キャンセル
            </button>
          </div>
        </div>
      )}
    </div>
  );
}