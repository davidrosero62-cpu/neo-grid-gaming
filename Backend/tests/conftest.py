def pytest_configure(config):
    sugar = config.pluginmanager.get_plugin('sugar')
    if sugar:
        original_status = sugar.pytest_report_teststatus
        
        def custom_status(report):
            if report.when == 'call':
                if report.passed:
                    return report.outcome, '✔ ✅ PERFECTO', '✅ PERFECTO'
                elif report.failed:
                    return report.outcome, '✘ ❌ FALLÓ', '❌ FALLÓ'
            return original_status(report)
            
        sugar.pytest_report_teststatus = custom_status