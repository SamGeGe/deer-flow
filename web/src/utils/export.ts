import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { Document, Packer, Paragraph, TextRun, HeadingLevel } from 'docx';
import { saveAs } from 'file-saver';

export type ExportFormat = 'markdown' | 'pdf' | 'word';

interface ExportOptions {
  filename: string;
  content: string;
  format: ExportFormat;
  element?: HTMLElement; // For PDF export from rendered HTML
}

/**
 * 生成带时间戳的文件名
 */
function generateTimestampedFilename(basename: string, extension: string): string {
  const now = new Date();
  const pad = (n: number) => n.toString().padStart(2, '0');
  const timestamp = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}_${pad(now.getHours())}-${pad(now.getMinutes())}-${pad(now.getSeconds())}`;
  return `${basename}-${timestamp}.${extension}`;
}

/**
 * 导出为Markdown格式
 */
export function exportAsMarkdown(content: string, filename?: string): void {
  const finalFilename = filename || generateTimestampedFilename('research-report', 'md');
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
  saveAs(blob, finalFilename);
}

/**
 * 从HTML元素导出为PDF格式，保持样式
 */
export async function exportAsPDFFromElement(element: HTMLElement, filename?: string): Promise<void> {
  try {
    const finalFilename = filename || generateTimestampedFilename('research-report', 'pdf');
    
    // 创建canvas
    const canvas = await html2canvas(element, {
      scale: 2, // 提高分辨率
      useCORS: true,
      allowTaint: false,
      backgroundColor: '#ffffff',
      removeContainer: true,
      logging: false,
      height: element.scrollHeight,
      width: element.scrollWidth,
    });

    const imgData = canvas.toDataURL('image/png');
    
    // 计算PDF尺寸
    const imgWidth = 210; // A4宽度(mm)
    const pageHeight = 295; // A4高度(mm)
    const imgHeight = (canvas.height * imgWidth) / canvas.width;
    let heightLeft = imgHeight;

    const pdf = new jsPDF('p', 'mm', 'a4');
    let position = 0;

    // 添加第一页
    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;

    // 如果内容超过一页，添加更多页面
    while (heightLeft >= 0) {
      position = heightLeft - imgHeight;
      pdf.addPage();
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;
    }

    pdf.save(finalFilename);
  } catch (error) {
    console.error('PDF导出失败:', error);
    throw new Error('PDF导出失败，请重试');
  }
}

/**
 * 使用浏览器打印功能导出PDF（保持更好的样式）
 */
export function exportAsPDFViaPrint(element: HTMLElement, filename?: string): void {
  const finalFilename = filename || generateTimestampedFilename('research-report', 'pdf');
  
  // 创建新窗口
  const printWindow = window.open('', '_blank');
  if (!printWindow) {
    throw new Error('无法打开打印窗口，请检查浏览器弹窗设置');
  }

  // 复制样式和内容到新窗口
  const html = `
    <!DOCTYPE html>
    <html>
      <head>
        <title>${finalFilename}</title>
        <meta charset="utf-8">
        <style>
          body {
            font-family: system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: none;
            margin: 0;
            padding: 20px;
            background: white;
          }
          
          h1, h2, h3, h4, h5, h6 {
            color: #2d3748;
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
          }
          
          h1 { font-size: 2em; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px; }
          h2 { font-size: 1.5em; }
          h3 { font-size: 1.25em; }
          
          p {
            margin-bottom: 16px;
          }
          
          ul, ol {
            margin-bottom: 16px;
            padding-left: 24px;
          }
          
          li {
            margin-bottom: 4px;
          }
          
          blockquote {
            border-left: 4px solid #e2e8f0;
            padding-left: 16px;
            margin: 16px 0;
            color: #4a5568;
            font-style: italic;
          }
          
          code {
            background-color: #f7fafc;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
          }
          
          pre {
            background-color: #f7fafc;
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 16px 0;
          }
          
          table {
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
          }
          
          th, td {
            border: 1px solid #e2e8f0;
            padding: 8px 12px;
            text-align: left;
          }
          
          th {
            background-color: #f7fafc;
            font-weight: 600;
          }
          
          a {
            color: #3182ce;
            text-decoration: none;
          }
          
          a:hover {
            text-decoration: underline;
          }
          
          @media print {
            body {
              padding: 0;
            }
            
            h1 {
              page-break-after: avoid;
            }
            
            h2, h3, h4, h5, h6 {
              page-break-after: avoid;
              page-break-inside: avoid;
            }
            
            table {
              page-break-inside: avoid;
            }
            
            ul, ol {
              page-break-inside: avoid;
            }
          }
        </style>
      </head>
      <body>
        ${element.innerHTML}
      </body>
    </html>
  `;

  printWindow.document.write(html);
  printWindow.document.close();

  // 等待内容加载后触发打印
  printWindow.onload = () => {
    printWindow.focus();
    printWindow.print();
    
    // 打印完成后关闭窗口
    setTimeout(() => {
      printWindow.close();
    }, 100);
  };
}

/**
 * 解析Markdown内容为结构化数据
 */
function parseMarkdownToStructuredContent(markdown: string) {
  const lines = markdown.split('\n');
  const content: any[] = [];
  
  for (let i = 0; i < lines.length; i++) {
    const lineText = lines[i];
    if (!lineText) continue;
    const line = lineText.trim();
    
    if (!line) {
      content.push(new Paragraph({ text: '', spacing: { after: 120 } }));
      continue;
    }
    
    // 标题处理
    if (line.startsWith('#')) {
      const headingMatch = line.match(/^#+/);
      const level = headingMatch ? headingMatch[0].length : 1;
      const text = line.replace(/^#+\s*/, '');
      
      const headingLevel = Math.min(level, 6) as 1 | 2 | 3 | 4 | 5 | 6;
      const headingLevelMap = {
        1: HeadingLevel.HEADING_1,
        2: HeadingLevel.HEADING_2,
        3: HeadingLevel.HEADING_3,
        4: HeadingLevel.HEADING_4,
        5: HeadingLevel.HEADING_5,
        6: HeadingLevel.HEADING_6,
      };
      
      content.push(new Paragraph({
        text,
        heading: headingLevelMap[headingLevel],
        spacing: { before: 240, after: 120 }
      }));
      continue;
    }
    
    // 列表处理
    if (line.startsWith('- ') || line.startsWith('* ') || /^\d+\.\s/.test(line)) {
      const text = line.replace(/^[-*]\s/, '').replace(/^\d+\.\s/, '');
      content.push(new Paragraph({
        text: `• ${text}`,
        spacing: { after: 60 },
        indent: { left: 360 }
      }));
      continue;
    }
    
    // 普通段落
    content.push(new Paragraph({
      children: [new TextRun(line)],
      spacing: { after: 120 }
    }));
  }
  
  return content;
}

/**
 * 导出为Word格式
 */
export async function exportAsWord(content: string, filename?: string): Promise<void> {
  try {
    const finalFilename = filename || generateTimestampedFilename('research-report', 'docx');
    
    // 解析Markdown内容
    const documentContent = parseMarkdownToStructuredContent(content);
    
    // 创建Word文档
    const doc = new Document({
      sections: [{
        properties: {},
        children: documentContent,
      }],
    });

    // 生成并下载
    const buffer = await Packer.toBuffer(doc);
    const blob = new Blob([buffer], { 
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' 
    });
    
    saveAs(blob, finalFilename);
  } catch (error) {
    console.error('Word导出失败:', error);
    throw new Error('Word导出失败，请重试');
  }
}

/**
 * 统一的导出函数
 */
export async function exportReport(options: ExportOptions): Promise<void> {
  const { format, content, filename, element } = options;
  
  try {
    switch (format) {
      case 'markdown':
        exportAsMarkdown(content, filename);
        break;
        
      case 'pdf':
        if (element) {
          exportAsPDFViaPrint(element, filename);
        } else {
          throw new Error('PDF导出需要提供HTML元素');
        }
        break;
        
      case 'word':
        await exportAsWord(content, filename);
        break;
        
      default:
        throw new Error(`不支持的导出格式: ${format}`);
    }
  } catch (error) {
    console.error(`${format}导出失败:`, error);
    throw error;
  }
} 