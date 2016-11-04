import subprocess

from checks import AgentCheck


class QShapeTranslator():
	def __init__(self, queue_type):
		self.queue_type = queue_type
		self.translated_domains = []
		self._stdout, self._stderr = self.__inspect_queue()

	def append_domains(self, domains):
		for domain in domains:
			domain_list = self.domain_list(domain)
			domain_dict = self.domain_dict(domain_list)
			self.translated_domains.append(domain_dict)

	def domains(self):
		raw_data = self._stdout.split('\n')[2:]
		raw_domains = self.__scrubbed_list(raw_data)
	 	return [raw_domain.strip() for raw_domain in raw_domains]

	def domain_dict(self, domain_list):
		return {'name': domain_list[0], 'total': domain_list[1],
                        'total_5': domain_list[2], 'total_10': domain_list[3],
                        'total_20': domain_list[4], 'total_40': domain_list[5],
                        'total_80': domain_list[6], 'total_160': domain_list[7],
                        'total_320': domain_list[8], 'total_640': domain_list[9],
                        'total_1280': domain_list[10], 'total_1280+': domain_list[11]}

	def domain_list(self, domain):
		raw_list = domain.strip().split(' ')
		return self.__scrubbed_list(raw_list)


	def translate(self):
		if self._stderr != '':
			raise ChildProcessError(self._stderr)
		elif self._stdout != '':
			domains = self.domains()
			return self.append_domains(domains)

	def qshape_command(self):
		return 'sudo /usr/sbin/qshape {qt}'.format(qt=self.queue_type)

	def __inspect_queue(self):
		command = self.qshape_command()
		process = subprocess.Popen(command,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           shell=True)
		stdout, stderr = process.communicate()
		return (stdout, stderr)

	def __scrubbed_list(self, raw_list):
		return [datum for datum in raw_list if datum != '']

"""Measures the number of messages in the deferred queue for all domains.

WARNING: The dd-agent user needs to have passwordless sudo access for the
         'qshape' command, unless dd-agent is run as root (No!).

         Example sudoers entry:
           dd-agent ALL=(ALL) NOPASSWD:/usr/sbin/qshape
"""
class QShapeCheck(AgentCheck):
	def check(self, instance):
		qsdt = QShapeTranslator('deferred')
		qsdt.translate()
		self.__gauge_domains(qsdt.translated_domains)

	def __gauge_domains(self, domains):
		for domain in domains:
        		self.gauge('qshape.queue.total', int(domain['total']),
                                   device_name=domain['name'])
