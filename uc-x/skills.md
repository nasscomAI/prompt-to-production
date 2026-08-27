skills:

\- name: document\_reader

&nbsp; description: Reads one or multiple text or CSV documents.

&nbsp; input: List of file paths.

&nbsp; output: Dictionary with filename as key and content as value.

&nbsp; error\_handling: If a file is missing, skip and flag in result.



\- name: query\_processor

&nbsp; description: Processes user query and searches documents for answer.

&nbsp; input: Query string and document dictionary.

&nbsp; output: Answer string.

&nbsp; error\_handling: If answer cannot be found, return 'Cannot determine' and flag NEEDS\_REVIEW.



\- name: answer\_writer

&nbsp; description: Writes the answer to a text file.

&nbsp; input: Answer string and output file path.

&nbsp; output: File written with answer.

&nbsp; error\_handling: If writing fails, log error and flag FAILED.

