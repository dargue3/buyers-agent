You are tasked with analyzing a list of files from a real estate disclosure package and identifying which files are specifically worth the expensive process of parsing and saving. This task is crucial for efficiently processing important information from real estate documents. Filenames that contain the word "Disclosure" are generally just legal documents and are not important, but some due diligence on your part is required to identify the most critical files.

The following file types are particularly important, but may be named differently. Consider alternative names that could mean the same things:

<critical_files>

- Home inspection report (also known as property inspection)
- Termite inspection report (also known as mold and pest inspection, wood destroying pest and organism report)
- Natural hazard report
  </critical_files>

<other_helpful_files>

- Roof inspection
- Foundation inspection
  </other_helpful_files>

You will be provided with a list of files in CSV format. Each line represents a file with the following information:
fileId,filename,extension,fileSize

The fileId is a unique identifier you MUST use when referring to files in your response.

Here's the list of files to analyze:
<file_list>
{fileList}
</file_list>

Analyze each file in the list and determine its importance based on the following criteria:

1. Does the filename match or closely resemble one of the important file types mentioned above?
2. Is the file a PDF? (Check the extension)
3. Is the file size (fileSize) reasonable for a detailed report? (Generally, important reports are typically at least a few hundred kilobytes in size)

For each file that you believe is important and worth parsing, provide your reasoning in the following format:
<file_analysis>
FileId: [fileId]
Filename: [filename]
Reasoning: [Your explanation of why this file is important]
</file_analysis>

After analyzing all files, provide your final selection of important files to be parsed in the following format:
<important_files>
[List of fileIds, one per line]
</important_files>

After listing the important files, identify any critical documents that appear to be missing from the provided list:
<missing_files>
[List each type of important document (from the list above) that was not found in any form, explaining what to look for]
</missing_files>

Remember to consider alternative names for the important file types and use your best judgment to identify files that are likely to contain crucial information for the real estate disclosure package.
