window.addEventListener('DOMContentLoaded', (event) => {
	[...document.getElementById('vendorDirectories').getElementsByTagName('details')].forEach(details => {
		[...details.getElementsByTagName('li')].forEach(li => { li.innerHTML = li.innerHTML.replace(/([^\/]+$)/m, '<span class="vendor">$&</span>'); });
	});
	[...document.querySelectorAll("[data-issue='CustomPackageNameIssue'] .issue-detail, [data-issue='StandardPackageNameIssue'] .issue-detail")].forEach(detail => {
		[...detail.getElementsByTagName('li')].forEach(li => { li.innerHTML = li.innerHTML.replace(/^([A-Z]+)/m, '<span class="prefix">$&</span>'); });
	});
	[...document.querySelectorAll("[data-issue='AtypicalImageFilesInTexturesDirectoryIssue'] .issue-detail, [data-issue='AtypicalImageFilesInTemplatesDirectoryIssue'] .issue-detail")].forEach(detail => {
		[...detail.getElementsByTagName('li')].forEach(li => { li.innerHTML = li.innerHTML.replace(/([^\/\.]+$)/m, '<span class="extension">$&</span>'); });
	});
	[...document.querySelectorAll("[data-issue='FullExtensionTipFilesIssue'] .issue-detail")].forEach(detail => {
		[...detail.getElementsByTagName('li')].forEach(li => { li.innerHTML = li.innerHTML.replace(/(\.[^\/\.]+)(?=\.tip\.png$)/i, '<span class="extension">$&</span>'); });
	});
});